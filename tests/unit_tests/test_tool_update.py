"""Tool-update loop and compact taxonomy view — scripted fake models, no API calls."""

import asyncio

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from taxonomy_generator.taxonomy_editor import TaxonomyEditor
from taxonomy_generator.tool_update import (
    TOOL_NAMES,
    TurnState,
    make_tools,
    run_tool_update,
)
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
    clusters, explanation, transcript = asyncio.run(
        run_tool_update(model, editor, [HumanMessage("update")], max_steps=max_steps, config=config))
    editor.transcript = transcript
    return editor, clusters, explanation


def test_langchain_tools_cover_every_editor_tool():
    from langchain_core.tools import BaseTool

    editor = TaxonomyEditor([], batch_doc_ids=[])
    tools = make_tools(editor, TurnState())
    assert all(isinstance(t, BaseTool) for t in tools)
    assert [t.name for t in tools] == list(TOOL_NAMES)
    assert set(TOOL_NAMES) == set(editor._tools)
    add_value = next(t for t in tools if t.name == "add_value")
    assert "Add a candidate decision" in add_value.description
    required = set(add_value.tool_call_schema.model_json_schema()["required"])
    assert {"dimension_id", "label", "status", "doc_ids", "reason"} <= required


def _invoke_tool(editor, name, args, cid="c1"):
    tool = next(t for t in make_tools(editor, TurnState()) if t.name == name)
    return tool.invoke({"name": name, "args": args, "id": cid, "type": "tool_call"})


def test_tool_invoke_returns_tool_messages_with_status():
    editor = TaxonomyEditor(_taxonomy(), batch_doc_ids=["d1", "d2"])
    ok = _invoke_tool(editor, "add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"})
    assert isinstance(ok, ToolMessage) and ok.status == "success" and ok.tool_call_id == "c1"
    bad = _invoke_tool(editor, "add_evidence", {"value_id": "9.9", "doc_ids": ["d2"], "reason": "r"})
    assert bad.status == "error" and "unknown value id" in bad.content


def test_schema_validation_errors_become_error_messages_and_are_logged():
    editor = TaxonomyEditor(_taxonomy(), batch_doc_ids=["d1", "d2"])
    msg = _invoke_tool(editor, "add_value", {"dimension_id": "2", "label": "X", "description": "", "status": "maybe",
                                             "doc_ids": ["d2"], "reason": "r"})
    assert msg.status == "error" and "status" in msg.content
    assert editor.rejected[-1]["tool"] == "add_value"


def test_numeric_ids_and_nested_split_parts_reach_the_editor_as_plain_values():
    editor = TaxonomyEditor(_taxonomy(), batch_doc_ids=["d1", "d2"])
    assert _invoke_tool(editor, "add_evidence", {"value_id": 1.1, "doc_ids": ["d2"], "reason": "r"}).status == "success"
    _invoke_tool(editor, "add_value", {"dimension_id": "1", "label": "KS test", "description": "", "status": "rejected",
                                       "doc_ids": ["d2"], "reason": "r"})
    _invoke_tool(editor, "add_value", {"dimension_id": "1", "label": "Mean test", "description": "", "status": "accepted",
                                       "doc_ids": ["d2"], "reason": "r"})
    _invoke_tool(editor, "add_value", {"dimension_id": "1", "label": "Page-Hinkley", "description": "",
                                       "status": "rejected", "doc_ids": ["d2"], "reason": "r"})
    msg = _invoke_tool(editor, "split_dimension", {"dimension_id": "1", "reason": "two questions", "parts": [
        {"name": "A", "description": "a", "value_ids": ["1.1", "1.2"]},
        {"name": "B", "description": "b", "value_ids": ["1.3", "1.4"]}]})
    assert msg.status == "success", msg.content


def test_transcript_records_model_turns_and_tool_replies():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c1"),
        call("finish", {"explanation": "done"}, "c2")])])
    editor, _, _ = _run(model)
    roles = [m["role"] for m in editor.transcript]
    assert roles == ["assistant", "tool", "tool"]
    assert editor.transcript[0]["tool_calls"][0]["name"] == "add_evidence"
    assert editor.transcript[1] == {"role": "tool", "tool_call_id": "c1", "status": "success",
                                    "content": editor.transcript[1]["content"]}
    assert "HumanMessage" not in str(editor.transcript)  # the prompt itself is not repeated


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
    model = ScriptedModel([bad, AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c1"),
        call("finish", {"explanation": "ok"}, "c2")])])
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
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c0"),
        call("finish", {"explanation": "ok"}, "c1")])],
                          reject_parallel=True)
    _editor, _, explanation = _run(model)
    assert explanation == "ok"
    assert model.bind_kwargs[-1].get("parallel_tool_calls") is None


def test_finish_is_handled_after_the_other_calls_of_its_turn():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("finish", {"explanation": "done"}, "c1"),
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c2")])])
    editor, clusters, explanation = _run(model)
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1", "d2"]
    assert len(editor.operations) == 1 and explanation == "done"


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


def test_openai_chat_models_are_bound_through_the_responses_api(monkeypatch):
    from langchain_openai import ChatOpenAI

    from taxonomy_generator.tool_update import _bind

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    tools = make_tools(TaxonomyEditor([], batch_doc_ids=[]), TurnState())
    bound = _bind(ChatOpenAI(model="gpt-5.6-luna"), tools, parallel=True)
    assert bound.bound.use_responses_api is True
    assert bound.kwargs["parallel_tool_calls"] is True and len(bound.kwargs["tools"]) == len(tools)


# ---------------------------------------------------------------- review fixes


def test_finish_is_refused_when_a_call_of_the_same_turn_failed():
    model = ScriptedModel([
        AIMessage(content="", tool_calls=[
            call("finish", {"explanation": "early"}, "c0"),
            call("add_evidence", {"value_id": "9.9", "doc_ids": ["d2"], "reason": "r"}, "c1"),
            call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c2")]),
        AIMessage(content="", tool_calls=[call("finish", {"explanation": "done"}, "c3")])])
    editor, clusters, explanation = _run(model)
    replies = {m.tool_call_id: m.content for m in model.inputs[1] if isinstance(m, ToolMessage)}
    assert "not finished" in replies["c0"] and "1 call" in replies["c0"]
    assert clusters[0]["values"][0]["supporting_doc_ids"] == ["d1", "d2"]  # the valid call still applied
    assert explanation == "done" and editor.stop == "finish"


def test_finish_with_uncited_documents_gets_one_reminder():
    model = ScriptedModel([
        AIMessage(content="", tool_calls=[call("finish", {"explanation": "first"}, "c1")]),
        AIMessage(content="", tool_calls=[call("finish", {"explanation": "d2 is irrelevant"}, "c2")])])
    editor, _, explanation = _run(model)
    reply = next(m for m in model.inputs[1] if isinstance(m, ToolMessage)).content
    assert "not finished" in reply and "d2" in reply
    assert explanation == "d2 is irrelevant" and model_calls(model) == 2


def model_calls(model):
    return len(model.inputs)


def test_a_turn_without_tool_calls_gets_one_nudge_then_ends():
    model = ScriptedModel([AIMessage(content="thinking"), AIMessage(content="still nothing")])
    editor, _, explanation = _run(model)
    assert model_calls(model) == 2
    assert any(isinstance(m, HumanMessage) and "finish" in m.content for m in model.inputs[1])
    assert editor.stop == "no_tool_call" and "no tool call" in explanation


def test_stop_reasons_are_recorded():
    _editor, _, _ = _run(ScriptedModel([AIMessage(content="", tool_calls=[call("finish", {"explanation": "x"}, "c")])]))
    turns = [AIMessage(content="", tool_calls=[call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"],
                                                                    "reason": "r"}, f"c{i}")]) for i in range(3)]
    editor, _, _ = _run(ScriptedModel(turns), max_steps=2)
    assert editor.stop == "step_limit"
    editor, _, _ = _run(ScriptedModel([], fail_at=1))
    assert editor.stop == "model_error"


def test_invalid_call_without_id_gets_no_reply_but_is_logged():
    bad = AIMessage(content="", invalid_tool_calls=[
        {"name": "add_value", "args": "{", "id": None, "error": "bad", "type": "invalid_tool_call"}])
    model = ScriptedModel([bad, AIMessage(content="", tool_calls=[call("finish", {"explanation": "ok"}, "c2")])])
    editor, _, _ = _run(model)
    assert not [m for m in model.inputs[1] if isinstance(m, ToolMessage)]
    assert editor.rejected[0]["tool"] == "add_value"


# ---------------------------------------------------------------- M2: structural check at finish


def test_finish_after_creating_dimensions_gets_one_structural_check():
    model = ScriptedModel([
        AIMessage(content="", tool_calls=[
            call("add_dimension", {"name": "Alert Routing", "description": "Where do alerts go?", "reason": "r"}, "c1"),
            call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c2"),
            call("finish", {"explanation": "first"}, "c3")]),
        AIMessage(content="", tool_calls=[call("finish", {"explanation": "dimensions answer different questions"},
                                               "c4")])])
    editor, _, explanation = _run(model)
    reply = next(m.content for m in model.inputs[1] if isinstance(m, ToolMessage) and m.tool_call_id == "c3")
    assert "not finished" in reply and "structural check" in reply
    assert "[1] Drift Test" in reply and "Alert Routing" in reply and "merge_dimensions" in reply
    assert explanation == "dimensions answer different questions" and editor.stop == "finish"


def test_no_structural_check_when_no_dimension_was_created():
    model = ScriptedModel([AIMessage(content="", tool_calls=[
        call("add_evidence", {"value_id": "1.1", "doc_ids": ["d2"], "reason": "r"}, "c1"),
        call("finish", {"explanation": "done"}, "c2")])])
    _editor, _, explanation = _run(model)
    assert explanation == "done"
