"""Tool-update loop and compact taxonomy view — scripted fake models, no API calls."""

import asyncio

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from taxonomy_generator.taxonomy_editor import TaxonomyEditor
from taxonomy_generator.tool_update import TOOL_NAMES, TOOL_SCHEMAS, run_tool_update
from taxonomy_generator.utils import format_taxonomy_compact


class ScriptedModel:
    """Returns predefined AIMessages in order; records what it was sent and how it was bound."""

    def __init__(self, replies, fail_at=None, reject_parallel=False):
        self.replies = list(replies)
        self.fail_at = fail_at
        self.reject_parallel = reject_parallel
        self.inputs, self.configs, self.bind_kwargs = [], [], []
        self.calls = 0
        self._parallel = None

    def bind_tools(self, tools, **kwargs):
        self.bind_kwargs.append(kwargs)
        self._parallel = kwargs.get("parallel_tool_calls")
        self.tools = tools
        return self

    async def ainvoke(self, messages, config=None):
        self.calls += 1
        self.inputs.append(list(messages))
        self.configs.append(config)
        if self.reject_parallel and self._parallel:
            raise ValueError("Unsupported parameter: 'parallel_tool_calls'")
        if self.fail_at is not None and self.calls == self.fail_at:
            raise RuntimeError("API down")
        return self.replies.pop(0) if self.replies else AIMessage(content="done")


def call(name, args, cid):
    return {"name": name, "args": args, "id": cid, "type": "tool_call"}


def _taxonomy():
    return [{"id": "1", "name": "Drift Test", "description": "Which test detects drift?",
             "relations": [{"target_id": "2", "type": "consequence", "rationale": "r"}],
             "values": [{"id": "1.1", "dimension_id": "1", "label": "CUSUM chart", "description": "cumulative sums",
                         "supporting_doc_ids": ["d1"], "status": "accepted"}]},
            {"id": "2", "name": "Response", "description": "How to respond?", "relations": [], "values": []}]


def _run(model, max_steps=8, config=None):
    editor = TaxonomyEditor(_taxonomy(), batch_doc_ids=["d1", "d2"])
    clusters, explanation = asyncio.run(
        run_tool_update(model, editor, [HumanMessage("update")], max_steps=max_steps, config=config))
    return editor, clusters, explanation


def test_tool_schemas_cover_every_editor_tool():
    names = [t["function"]["name"] for t in TOOL_SCHEMAS]
    assert names == list(TOOL_NAMES)
    editor = TaxonomyEditor([], batch_doc_ids=[])
    assert set(names) == set(editor._tools)
    add_value = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "add_value")["function"]
    assert {"dimension_id", "label", "status", "doc_ids", "reason"} <= set(add_value["parameters"]["required"])


def test_parallel_calls_and_finish_in_one_turn():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_value", {"dimension_id": "2", "label": "Rollback", "description": "revert", "status": "accepted",
                           "doc_ids": ["d2"], "reason": "d2 rolls back"}, "c1"),
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "d2 uses CUSUM"}, "c2"),
        call("finish", {"explanation": "Added Rollback; cited d2 for CUSUM."}, "c3")])])
    editor, clusters, explanation = _run(model)
    assert model.calls == 1
    assert model.bind_kwargs[0].get("parallel_tool_calls") is True
    assert explanation == "Added Rollback; cited d2 for CUSUM."
    assert [v["label"] for v in clusters[1]["values"]] == ["Rollback"]
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1", "d2"]
    assert len(editor.operations) == 2 and editor.uncited == []


def test_invalid_call_error_reaches_the_model_and_the_correction_applies():
    model = ScriptedModel([
        AIMessage(content="", tool_calls=[call("add_evidence", {"value_id": "9.9", "doc_ids": ["d2"], "reason": "r"},
                                               "c1")]),
        AIMessage(content="", tool_calls=[call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"},
                                               "c2"), call("finish", {"explanation": "fixed"}, "c3")]),
    ])
    editor, clusters, _ = _run(model)
    second_input = model.inputs[1]
    tool_msgs = [m for m in second_input if isinstance(m, ToolMessage)]
    assert tool_msgs and "unknown value id" in tool_msgs[0].content and tool_msgs[0].tool_call_id == "c1"
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1", "d2"]
    assert len(editor.rejected) == 1


def test_unparsable_tool_call_gets_an_error_reply_and_the_loop_continues():
    bad = AIMessage(content="", invalid_tool_calls=[
        {"name": "add_value", "args": "{not json", "id": "bad1", "error": "JSONDecodeError", "type": "invalid_tool_call"}])
    model = ScriptedModel([bad, AIMessage(content="", tool_calls=[call("finish", {"explanation": "ok"}, "c2")])])
    editor, _, explanation = _run(model)
    replies = [m for m in model.inputs[1] if isinstance(m, ToolMessage)]
    assert replies[0].tool_call_id == "bad1" and "could not parse" in replies[0].content
    assert editor.rejected[0]["tool"] == "add_value"
    assert explanation == "ok"


def test_no_tool_calls_returns_previous_taxonomy_and_fallback_explanation():
    editor, clusters, explanation = _run(ScriptedModel([AIMessage(content="nothing to change")]))
    assert clusters == _taxonomy()
    assert "no operations" in explanation.lower()


def test_step_limit_keeps_applied_operations():
    turns = [AIMessage(content="", tool_calls=[call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"],
                                                                    "reason": "r"}, f"c{i}")]) for i in range(5)]
    model = ScriptedModel(turns)
    editor, clusters, explanation = _run(model, max_steps=2)
    assert model.calls == 2
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1", "d2"]
    assert "step limit" in explanation


def test_model_error_after_a_turn_keeps_that_turns_operations():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_value", {"dimension_id": "2", "label": "Rollback", "description": "", "status": "accepted",
                           "doc_ids": ["d2"], "reason": "r"}, "c1")])], fail_at=2)
    editor, clusters, explanation = _run(model)
    assert [v["label"] for v in clusters[1]["values"]] == ["Rollback"]
    assert "model call failed" in explanation


def test_parallel_tool_calls_rejected_by_the_api_rebinds_without_it():
    model = ScriptedModel([AIMessage(content="", tool_calls=[call("finish", {"explanation": "ok"}, "c1")])],
                          reject_parallel=True)
    _editor, _, explanation = _run(model)
    assert explanation == "ok"
    assert model.bind_kwargs[-1].get("parallel_tool_calls") is None


def test_calls_after_finish_are_answered_but_not_applied():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("finish", {"explanation": "done"}, "c1"),
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c2")])])
    editor, clusters, _ = _run(model)
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1"]
    assert editor.operations == []


def test_the_node_config_reaches_every_model_call():
    class Recorder(AsyncCallbackHandler):
        pass

    config = {"callbacks": [Recorder()], "run_name": "x"}
    model = ScriptedModel([AIMessage(content="", tool_calls=[call("add_evidence", {"value_id": "1.1",
                                                                                  "doc_ids": ["d2"], "reason": "r"},
                                                                  "c1")]),
                           AIMessage(content="", tool_calls=[call("finish", {"explanation": "ok"}, "c2")])])
    _run(model, config=config)
    assert model.configs == [config, config]


def test_compact_view_shows_ids_names_statuses_relations_and_hides_descriptions_and_provenance():
    text = format_taxonomy_compact(_taxonomy())
    assert "[1] Drift Test — Which test detects drift? (consequence → 2)" in text
    assert "1.1 CUSUM chart (accepted)" in text
    assert "cumulative sums" not in text and "d1" not in text
    assert "[2] Response — How to respond? (no values yet)" in text
