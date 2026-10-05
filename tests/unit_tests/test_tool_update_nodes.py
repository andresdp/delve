"""update_taxonomy / review_taxonomy in the three edit modes, and the restore step — no API calls."""

import asyncio
import dataclasses
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage

from taxonomy_generator.nodes import taxonomy_reviewer, taxonomy_updater
from taxonomy_generator.state import OutputState, State
from taxonomy_generator.utils import restore_dropped_values


class ScriptedModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.inputs = []

    def bind_tools(self, tools, **kwargs):
        return self

    async def ainvoke(self, messages, config=None):
        self.inputs.append(list(messages))
        return self.replies.pop(0) if self.replies else AIMessage(content="done")


def call(name, args, cid):
    return {"name": name, "args": args, "id": cid, "type": "tool_call"}


def _doc(doc_id):
    return {"id": doc_id, "content": f"content {doc_id}", "summary": f"summary {doc_id}"}


TAXONOMY = [{"id": "1", "name": "Drift Test", "description": "Which test?", "relations": [], "values": [
    {"id": "1.1", "dimension_id": "1", "label": "CUSUM chart", "description": "x", "supporting_doc_ids": ["d1"],
     "status": "accepted"},
    {"id": "1.2", "dimension_id": "1", "label": "KS test", "description": "y", "supporting_doc_ids": [],
     "status": "rejected"}]}]


def _state():
    return State(documents=[_doc("d1"), _doc("d2")], clusters=[TAXONOMY], minibatches=[[0], [1]],
                 open_code_batch_index=2,
                 open_codes=[{"doc_id": "d2", "label": "Page-Hinkley", "rationale": "r", "status": "accepted"}])


def _config(**overrides):
    return {"configurable": {"mode": "train", "visualization_enabled": False, **overrides}}


def _run_update(model, mode="tools", **overrides):
    with patch.object(taxonomy_updater, "load_chat_model", return_value=model):
        return asyncio.run(taxonomy_updater.update_taxonomy(_state(), _config(edit_mode=mode, **overrides)))


FINISH_TURN = AIMessage(content="", tool_calls=[
    call("add_value", {"dimension_id": "1", "label": "Page-Hinkley", "description": "change point",
                       "status": "accepted", "doc_ids": ["d2"], "reason": "d2"}, "c1"),
    call("finish", {"explanation": "Added Page-Hinkley from d2."}, "c2")])


def test_rewrite_mode_uses_the_chain_and_returns_no_operation_log():
    fake = {"clusters": [TAXONOMY], "explanations": ["e"], "status": ["s"]}
    with patch.object(taxonomy_updater, "invoke_taxonomy_chain", new=AsyncMock(return_value=fake)) as chain:
        result = asyncio.run(taxonomy_updater.update_taxonomy(_state(), _config(edit_mode="rewrite")))
    assert chain.await_count == 1
    assert result == fake and "operation_log" not in result


def test_tools_mode_returns_rewrite_shapes_plus_one_operation_log_entry():
    model = ScriptedModel([FINISH_TURN])
    result = _run_update(model)
    assert set(result) == {"clusters", "explanations", "status", "operation_log"}
    clusters = result["clusters"][0]
    assert [v["label"] for v in clusters[0]["values"]] == ["CUSUM chart", "KS test", "Page-Hinkley"]
    assert result["explanations"] == ["Added Page-Hinkley from d2."]
    (entry,) = result["operation_log"]
    assert entry["node"] == "update_taxonomy" and entry["iteration"] == 2 and entry["edit_mode"] == "tools"
    assert [op["tool"] for op in entry["operations"]] == ["add_value"]
    # the prompt carried the compact view and the batch's open codes, not the full JSON
    system = model.inputs[0][0].content
    assert "1.1 CUSUM chart (accepted)" in system and "Page-Hinkley" in model.inputs[0][0].content


def test_tools_mode_validates_evidence_against_the_minibatch():
    bad = AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d1"], "reason": "r"}, "c1"),
        call("finish", {"explanation": "x"}, "c2")])
    result = _run_update(ScriptedModel([bad]))
    (entry,) = result["operation_log"]
    assert entry["operations"] == [] and "not documents of this batch" in entry["rejected"][0]["error"]


def test_tools_review_uses_the_review_sample_documents():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d1"], "reason": "r"}, "c1"),
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c2"),
        call("finish", {"explanation": "ok"}, "c3")])])
    with patch.object(taxonomy_reviewer, "load_chat_model", return_value=model), \
         patch.object(taxonomy_reviewer.random, "shuffle", lambda x: None):
        result = asyncio.run(taxonomy_reviewer.review_taxonomy(
            _state(), _config(edit_mode="tools", review_sample_size=1)))
    (entry,) = result["operation_log"]
    assert entry["node"] == "review_taxonomy"
    assert len(entry["operations"]) == 1 and len(entry["rejected"]) == 1  # d2 is not in the sample [d1]


def test_tools_mode_biplot_index_anticipates_own_append():
    with patch.object(taxonomy_updater, "load_chat_model", return_value=ScriptedModel([FINISH_TURN])), \
         patch.object(taxonomy_updater, "render_taxonomy_biplot", new=AsyncMock(return_value=None)) as render:
        asyncio.run(taxonomy_updater.update_taxonomy(_state(), _config(edit_mode="tools")))
    assert render.call_args.kwargs["iteration_index"] == 2


def test_operation_log_is_declared_on_the_output_state():
    assert "operation_log" in {f.name for f in dataclasses.fields(OutputState)}
    assert "operation_log" in {f.name for f in dataclasses.fields(State)}


# ---------------------------------------------------------------- rewrite_restore


def test_rewrite_restore_puts_back_dropped_supported_values():
    rewritten = [{"id": "1", "name": "Drift Test", "description": "Which test?", "relations": [], "values": [
        {"id": "1.1", "dimension_id": "1", "label": "Page-Hinkley", "description": "z", "supporting_doc_ids": ["d2"],
         "status": "accepted"}]}]
    fake = {"clusters": [rewritten], "explanations": ["rewrote"], "status": ["s"]}
    with patch.object(taxonomy_updater, "invoke_taxonomy_chain", new=AsyncMock(return_value=fake)):
        result = asyncio.run(taxonomy_updater.update_taxonomy(_state(), _config(edit_mode="rewrite_restore")))
    labels = [v["label"] for v in result["clusters"][0][0]["values"]]
    assert labels == ["Page-Hinkley", "CUSUM chart"]  # KS test had no evidence: not restored
    (entry,) = result["operation_log"]
    assert entry["edit_mode"] == "rewrite_restore" and [r["label"] for r in entry["restored"]] == ["CUSUM chart"]
    assert "Restored 1" in result["explanations"][0]


def test_restore_keeps_values_the_rewrite_kept_and_recreates_a_dropped_dimension():
    previous = TAXONOMY + [{"id": "2", "name": "Response", "description": "How?", "relations": [], "values": [
        {"id": "2.1", "dimension_id": "2", "label": "Rollback", "description": "r", "supporting_doc_ids": ["d1"],
         "status": "accepted"}]}]
    updated = [{"id": "1", "name": "drift test", "description": "Which test?", "relations": [], "values": [
        {"id": "1.1", "dimension_id": "1", "label": "cusum chart", "description": "x", "supporting_doc_ids": ["d1"],
         "status": "accepted"}]}]
    clusters, restored = restore_dropped_values(previous, updated)
    assert [r["label"] for r in restored] == ["Rollback"]
    assert [v["label"] for v in clusters[0]["values"]] == ["cusum chart"]  # kept under a new spelling: not duplicated
    response = next(c for c in clusters if c["name"] == "Response")
    assert [v["label"] for v in response["values"]] == ["Rollback"]
    assert len({c["id"] for c in clusters}) == len(clusters)


def test_restore_with_nothing_dropped_is_a_no_op():
    clusters, restored = restore_dropped_values(TAXONOMY, TAXONOMY)
    assert restored == [] and clusters == TAXONOMY


def test_cli_summary_line_per_operation_log_entry():
    import main as main_module

    tools = {"edit_mode": "tools", "operations": [{}, {}], "rejected": [{}], "uncited": ["d9"]}
    assert main_module._operation_log_line(tools) == "2 operations applied, 1 rejected, 1 batch documents uncited"
    restore = {"edit_mode": "rewrite_restore", "restored": [{"label": "x"}]}
    assert main_module._operation_log_line(restore) == "restored 1 dropped evidence-backed values"


def test_saved_taxonomy_records_edit_mode_and_operation_log_in_order():
    import main as main_module

    data = {}
    main_module._add_edit_record(data, None, [])
    assert data == {"edit_mode": "rewrite"}
    entries = [{"iteration": 2, "node": "update_taxonomy"}, {"iteration": 3, "node": "review_taxonomy"}]
    main_module._add_edit_record(data, "tools", entries)
    assert data["edit_mode"] == "tools" and [e["iteration"] for e in data["operation_log"]] == [2, 3]


def test_review_in_rewrite_restore_mode_restores_and_logs():
    rewritten = [{"id": "1", "name": "Drift Test", "description": "Which test?", "relations": [], "values": []}]
    fake = {"clusters": [rewritten], "explanations": ["reviewed"], "status": ["s"]}
    with patch.object(taxonomy_reviewer, "invoke_taxonomy_chain", new=AsyncMock(return_value=fake)):
        result = asyncio.run(taxonomy_reviewer.review_taxonomy(_state(), _config(edit_mode="rewrite_restore")))
    (entry,) = result["operation_log"]
    assert entry["node"] == "review_taxonomy" and [r["label"] for r in entry["restored"]] == ["CUSUM chart"]


def test_restored_dimension_keeps_only_relations_it_can_still_point_to():
    previous = [
        {"id": "1", "name": "Drift Test", "description": "q", "relations": [], "values": []},
        {"id": "2", "name": "Response", "description": "q",
         "relations": [{"target_id": "1", "type": "consequence", "rationale": "r"},
                       {"target_id": "3", "type": "constrains", "rationale": "gone"}],
         "values": [{"id": "2.1", "dimension_id": "2", "label": "Rollback", "description": "",
                     "supporting_doc_ids": ["d1"], "status": "accepted"}]},
        {"id": "3", "name": "Old Topic", "description": "q", "relations": [], "values": []}]
    updated = [{"id": "7", "name": "Drift Test", "description": "q", "relations": [], "values": []}]
    clusters, _ = restore_dropped_values(previous, updated)
    response = next(c for c in clusters if c["name"] == "Response")
    assert response["relations"] == [{"target_id": "7", "type": "consequence", "rationale": "r"}]
