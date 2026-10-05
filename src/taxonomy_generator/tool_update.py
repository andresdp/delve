"""Tool-based taxonomy updates (``taxonomy.edit_mode: tools``): LangChain tools and the tool-calling loop.

The Taxonomist's coding operations are LangChain tools (``make_tools``): one
``StructuredTool`` per operation, with a Pydantic ``args_schema`` and a docstring
description, each bound to the update's ``TaxonomyEditor``. The generation LLM is
bound to them with ``bind_tools`` and called in turns, following LangChain's manual
tool-execution loop: every call in ``AIMessage.tool_calls`` is executed with
``tool.invoke(tool_call)``, which returns its ``ToolMessage`` (status ``success`` or
``error``), so the model can correct itself. Within a turn, calls run in the order
the model returned them (they depend on each other's ids), and ``finish`` runs last.
The loop ends when the model's ``finish`` is accepted, it twice answers without tool
calls, ``max_steps`` turns pass, or a model call fails; operations applied so far are
always kept (the taxonomy is never re-emitted). The model turns and tool replies are
returned as a transcript for the operation log.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from taxonomy_generator.schemas import DecisionStatus, RelationType
from taxonomy_generator.settings import TaxonomySettings
from taxonomy_generator.taxonomy_editor import TaxonomyEditor
from taxonomy_generator.utils import (
    format_taxonomy_compact,
    restore_dropped_values,
    taxonomy_prompt_inputs,
)

logger = logging.getLogger(__name__)

Reason = Field(description="Short justification of this change: the new data or feedback issue behind it.")


class _Args(BaseModel):
    """Base of the tool argument schemas: ids sent as numbers (3, 1.2) are read as strings."""

    model_config = ConfigDict(coerce_numbers_to_str=True)


class AddValue(_Args):
    """Add a candidate decision or outcome to a dimension, citing the batch documents that support it."""

    dimension_id: str = Field(description="Id of the dimension (e.g. '3').")
    label: str = Field(description="Noun phrase naming the decision or outcome; never prefixed with the status.")
    description: str = Field(description="What this value means along its dimension.")
    status: DecisionStatus = Field(
        description="accepted: adopted; rejected: explicitly declined; outcome: an effect, not a decision.")
    doc_ids: List[str] = Field(description="Ids of documents in this batch whose codes support the value.")
    reason: str = Reason


class AddEvidence(_Args):
    """Cite batch documents as further evidence for an existing value (same option, same status)."""

    value_id: str = Field(description="Id of the value (e.g. '3.2').")
    doc_ids: List[str] = Field(description="Ids of documents in this batch that support it.")
    reason: str = Reason


class MoveValue(_Args):
    """Move a value to the dimension whose question it answers (it gets a new id there)."""

    value_id: str
    to_dimension_id: str
    reason: str = Reason


class MergeValues(_Args):
    """Merge values of one dimension and identical status that name the same option."""

    value_ids: List[str] = Field(description="Two or more value ids; the first one is kept.")
    label: str
    description: str
    reason: str = Reason


class RelabelValue(_Args):
    """Rewrite a value's label (and optionally its description)."""

    value_id: str
    label: str
    description: str | None = None
    reason: str = Reason


class SetStatus(_Args):
    """Reclassify a value's status on direct evidence (cite the document id in the reason)."""

    value_id: str
    status: DecisionStatus
    reason: str = Reason


class RemoveValue(_Args):
    """Remove a value with no supporting documents (supported values cannot be removed)."""

    value_id: str
    reason: str = Reason


class AddDimension(_Args):
    """Open a new dimension (decision point); add its values in the next turn, using the returned id."""

    name: str = Field(description="Noun phrase naming the axis of variation.")
    description: str = Field(description="The one question the dimension's values answer.")
    reason: str = Reason


class RenameDimension(_Args):
    """Rename a dimension and optionally rewrite its description."""

    dimension_id: str
    name: str
    description: str | None = None
    reason: str = Reason


class SplitPart(_Args):
    """One part of a split."""

    name: str
    description: str
    value_ids: List[str]


class SplitDimension(_Args):
    """Split a dimension that bundles several questions; every part keeps at least two candidate decisions."""

    dimension_id: str
    parts: List[SplitPart] = Field(description="Two or more parts; every value goes to exactly one part.")
    reason: str = Reason


class MergeDimensions(_Args):
    """Merge dimensions that ask the same question; the first id is kept."""

    dimension_ids: List[str]
    name: str
    description: str
    reason: str = Field(description="The shared question that makes these dimensions one decision point.")


class RemoveDimension(_Args):
    """Remove an empty dimension (move its values first)."""

    dimension_id: str
    reason: str = Reason


class AddRelation(_Args):
    """Relate two dimensions when the use case's logic requires it."""

    source_id: str
    target_id: str
    type: RelationType = Field(description=(
        "precondition: a choice on the target is required before the source applies; consequence: choices on "
        "the source imply outcomes on the target; co_occurring: both appear together, neither causes the other; "
        "constrains: the source restricts the target's available choices."))
    rationale: str


class RemoveRelation(_Args):
    """Remove the relations from one dimension to another."""

    source_id: str
    target_id: str
    reason: str = Reason


class Finish(_Args):
    """End this update; the explanation names every operation applied and why."""

    explanation: str


TOOLS: list[tuple[str, type[BaseModel]]] = [
    ("add_value", AddValue), ("add_evidence", AddEvidence), ("move_value", MoveValue),
    ("merge_values", MergeValues), ("relabel_value", RelabelValue), ("set_status", SetStatus),
    ("remove_value", RemoveValue), ("add_dimension", AddDimension), ("rename_dimension", RenameDimension),
    ("split_dimension", SplitDimension), ("merge_dimensions", MergeDimensions),
    ("remove_dimension", RemoveDimension), ("add_relation", AddRelation), ("remove_relation", RemoveRelation),
    ("finish", Finish),
]
TOOL_NAMES = tuple(name for name, _ in TOOLS)


@dataclass
class TurnState:
    """What ``finish`` needs to know about the current turn and update."""

    failed: int = 0                  # calls of this turn that failed (finish is refused while > 0)
    reminded: bool = False           # the uncited-documents reminder was given once
    structure_checked: bool = False  # the structural check (after new dimensions) was asked once


def _plain(value: Any) -> Any:
    """Return validated arguments as plain values (nested schema objects, e.g. split parts, as dicts)."""
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def make_tools(editor: TaxonomyEditor, turn: TurnState) -> list[BaseTool]:
    """Build the coding operations as LangChain tools bound to ``editor`` (one set per update).

    A tool validates its arguments against its schema, applies the operation through
    ``editor.apply`` (which enforces the coding rules and rolls back a rejected call),
    and returns the editor's message; a rejected call raises ``ToolException``, which
    the tool turns into an error ``ToolMessage``. Schema violations are logged as
    rejected calls too.
    """
    def operation(name: str):
        def run(**kwargs: Any) -> str:
            args = {k: _plain(v) for k, v in kwargs.items() if v is not None}
            if name == "finish":
                return _finish_reply(editor, args, turn)
            ok, message = editor.apply(name, args)
            if not ok:
                raise ToolException(message)
            return message
        return run

    def invalid(name: str):
        def handle(error: ValidationError) -> str:
            problems = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors())
            message = f"error: invalid arguments ({problems})"
            editor.log_rejected(name, None, message)
            return message
        return handle

    return [StructuredTool.from_function(func=operation(name), name=name, args_schema=schema,
                                         description=(schema.__doc__ or "").strip(), handle_tool_error=True,
                                         handle_validation_error=invalid(name))
            for name, schema in TOOLS]


def _bind(model: Any, tools: list[BaseTool], parallel: bool) -> Any:
    """Bind the tools; OpenAI chat models go through the Responses API.

    Newer OpenAI reasoning models (e.g. gpt-5.6-luna) reject function tools on Chat
    Completions when a reasoning effort is set; the Responses API accepts them. No
    temperature or reasoning effort is set here.
    """
    if "use_responses_api" in getattr(type(model), "model_fields", {}):
        model = model.model_copy(update={"use_responses_api": True})
    return model.bind_tools(tools, parallel_tool_calls=True) if parallel else model.bind_tools(tools)


async def _invoke(model: Any, tools: list[BaseTool], bound: Any, parallel: bool, messages: list,
                  config: Any) -> tuple[Any, Any, bool, Any]:
    """Call the bound model once; on a parallel_tool_calls rejection rebind without it and retry once.

    Returns ``(ai_message or None, bound, parallel, error or None)``.
    """
    try:
        return await bound.ainvoke(messages, config=config), bound, parallel, None
    except Exception as exc:
        if not (parallel and "parallel_tool_calls" in str(exc)):
            return None, bound, parallel, exc
    logger.warning("Model rejects parallel_tool_calls; continuing with sequential tool calls")
    bound = _bind(model, tools, parallel=False)
    try:
        return await bound.ainvoke(messages, config=config), bound, False, None
    except Exception as exc:
        return None, bound, False, exc


STOP_TEXT = {
    "finish": "the model called finish",
    "no_tool_call": "the model made no tool call",
    "step_limit": "the step limit was reached",
    "model_error": "a model call failed",
}
NO_CALL_NUDGE = ("You made no tool call. Continue with the tools, or call finish with your explanation if the "
                 "update is complete.")


def fallback_explanation(editor: TaxonomyEditor, stop: str) -> str:
    """Explanation built from the log when the model did not call ``finish``."""
    counts = Counter(op["tool"] for op in editor.operations)
    if counts:
        applied = ", ".join(f"{n} {tool}" for tool, n in sorted(counts.items()))
        text = f"Applied {sum(counts.values())} operations ({applied})"
    else:
        text = "No operations applied; the taxonomy is unchanged"
    if editor.rejected:
        text += f"; {len(editor.rejected)} calls were rejected"
    return f"{text}. The update ended without finish: {STOP_TEXT.get(stop, stop)}."


def _finish_reply(editor: TaxonomyEditor, args: dict, turn: TurnState) -> str:
    """Reply to a finish call: refused while calls of the turn failed, reminded once of uncited documents."""
    if editor.finished:
        return "ignored: the update already finished"
    if turn.failed:
        n = turn.failed
        return (f"not finished: {n} call{'s' if n != 1 else ''} of this turn failed; fix "
                f"{'them' if n != 1 else 'it'} (see the errors above), then call finish again")
    uncited = editor.uncited_now()
    if uncited and not turn.reminded:
        turn.reminded = True
        return (f"not finished: batch documents {', '.join(uncited)} are cited by no value. Cite their codes with "
                "add_evidence or add_value, or call finish again if they are irrelevant to the use case")
    created = sum(op["tool"] in ("add_dimension", "split_dimension") for op in editor.operations)
    if created and not turn.structure_checked:
        turn.structure_checked = True
        listing = "; ".join(f"[{c['id']}] {c.get('name', '')} ({len(c['values'])} values)" for c in editor.clusters)
        return ("not finished: structural check. This update created dimensions. Current dimensions: "
                f"{listing}. If two or more of them answer parts of one design question (sibling decisions a "
                "designer would face as one choice), combine them with merge_dimensions; then call finish, or call "
                "finish again if every dimension is a distinct design decision")
    ok, message = editor.apply("finish", args)
    if not ok:
        raise ToolException(message)
    return message


def transcript_entries(messages: List[BaseMessage]) -> list[dict[str, Any]]:
    """Model turns, tool replies and nudges of one update, as JSON-ready records."""
    entries: list[dict[str, Any]] = []
    for m in messages:
        if isinstance(m, AIMessage):
            text = str(m.text)  # the text blocks of the turn (reasoning and tool calls are separate)
            entries.append({"role": "assistant", "text": text,
                            "tool_calls": [{"name": c["name"], "args": c.get("args"), "id": c.get("id")}
                                           for c in m.tool_calls or []],
                            "invalid_tool_calls": [{"name": c.get("name"), "args": c.get("args"), "id": c.get("id"),
                                                    "error": c.get("error")} for c in m.invalid_tool_calls or []]})
        elif isinstance(m, ToolMessage):
            entries.append({"role": "tool", "tool_call_id": m.tool_call_id, "status": m.status,
                            "content": m.content})
        else:
            entries.append({"role": "user", "content": m.content})
    return entries


async def run_tool_update(model: Any, editor: TaxonomyEditor, messages: List[BaseMessage], max_steps: int,
                          config: Any = None) -> tuple[list[dict], str, list[dict[str, Any]]]:
    """Run the tool loop on ``editor``; return the edited taxonomy, the explanation and the transcript.

    Within a turn, ``finish`` runs after the other calls and is accepted only when none
    of them failed; the first ``finish`` with uncited batch documents gets one reminder.
    A turn without tool calls gets one nudge. ``editor.stop`` records why the loop ended
    (``STOP_TEXT`` keys).
    """
    turn = TurnState()
    tools = make_tools(editor, turn)
    by_name = {t.name: t for t in tools}
    messages = list(messages)
    first_new = len(messages)
    parallel = True
    bound = _bind(model, tools, parallel)
    stop, nudged = "step_limit", False
    for step in range(max_steps):
        ai, bound, parallel, error = await _invoke(model, tools, bound, parallel, messages, config)
        if ai is None:
            logger.warning("Tool update: model call failed at turn %d (%s: %s); keeping %d applied operations",
                           step + 1, type(error).__name__, error, len(editor.operations))
            stop = "model_error"
            break
        if not isinstance(ai, AIMessage):
            ai = AIMessage(content=str(getattr(ai, "content", ai)))
        messages.append(ai)
        calls, invalid = ai.tool_calls or [], ai.invalid_tool_calls or []
        if not calls and not invalid:
            if nudged:
                stop = "no_tool_call"
                break
            nudged = True
            messages.append(HumanMessage(NO_CALL_NUDGE))
            continue
        turn.failed = 0
        for tc in calls:
            if tc["name"] == "finish":
                continue
            reply = _run_call(by_name, editor, tc, config)
            turn.failed += reply.status == "error"
            messages.append(reply)
        for bad in invalid:
            error = f"could not parse arguments: {bad.get('error') or 'invalid JSON'}"
            editor.log_rejected(bad.get("name") or "?", bad.get("args"), error)
            turn.failed += 1
            if bad.get("id"):  # every tool call id needs a reply, or the next request fails
                messages.append(ToolMessage(f"error: {error}", tool_call_id=bad["id"], status="error"))
        for tc in calls:
            if tc["name"] == "finish":
                messages.append(_run_call(by_name, editor, tc, config))
        if editor.finished:
            stop = "finish"
            break
    if stop == "step_limit":
        logger.warning("Tool update reached the step limit (%d turns); keeping %d applied operations",
                       max_steps, len(editor.operations))
    editor.stop = stop
    clusters = editor.result()
    explanation = editor.explanation if editor.finished else fallback_explanation(editor, stop)
    return clusters, explanation, transcript_entries(messages[first_new:])


def _run_call(by_name: dict[str, BaseTool], editor: TaxonomyEditor, tool_call: dict, config: Any) -> ToolMessage:
    """Execute one tool call with ``tool.invoke``; an unknown tool name gets an error reply."""
    tool = by_name.get(tool_call["name"])
    if tool is None:
        message = f"error: unknown tool '{tool_call['name']}'; available: {', '.join(by_name)}"
        editor.log_rejected(tool_call["name"], tool_call.get("args"), message)
        return ToolMessage(message, tool_call_id=tool_call["id"], status="error")
    return tool.invoke({**tool_call, "type": "tool_call"}, config=config)


def _doc_id(doc: Any) -> str:
    return str(doc["id"] if isinstance(doc, dict) else doc.id)


async def tool_mode_node(model: Any, prompt: Any, state: Any, config: Any, configuration: Any,
                         doc_indices: List[int], node: str) -> dict:
    """Run one tools-mode update or review; return the node result in the rewrite shapes plus its log entry.

    ``node`` is ``update_taxonomy`` or ``review_taxonomy``; the review may reclassify
    statuses without citing a document (its sample is the evidence).
    """
    review = node == "review_taxonomy"
    previous = state.clusters[-1] if state.clusters else []
    inputs = taxonomy_prompt_inputs(state, configuration, doc_indices, True, format_taxonomy_compact(previous))
    messages = prompt.format_messages(**inputs)
    editor = TaxonomyEditor(previous, [_doc_id(state.documents[i]) for i in doc_indices], review=review)
    max_steps = configuration.edit_max_steps or TaxonomySettings.edit_max_steps
    clusters, explanation, transcript = await run_tool_update(model, editor, messages, max_steps=max_steps,
                                                              config=config)
    entry = {"iteration": len(state.clusters) + 1, "node": node, "edit_mode": "tools", **editor.summary(),
             "explanation": explanation, "transcript": transcript}
    status = (f"Taxonomy edited with tools: {len(editor.operations)} operations applied, "
              f"{len(editor.rejected)} rejected, {len(editor.uncited)} batch documents uncited.")
    logger.info(status)
    return {"clusters": [clusters], "explanations": [explanation], "status": [status], "operation_log": [entry]}


def restore_after_rewrite(result: dict, state: Any, node: str) -> dict:
    """``rewrite_restore`` mode: put back evidence-backed values the rewrite dropped, and log them."""
    previous = state.clusters[-1] if state.clusters else []
    if not result.get("clusters"):
        return result
    clusters, restored = restore_dropped_values(previous, result["clusters"][0])
    note = (f"Restored {len(restored)} evidence-backed value{'s' if len(restored) != 1 else ''} the rewrite dropped"
            + (": " + "; ".join(r["label"] for r in restored) if restored else "") + ".")
    if restored:
        logger.info(note)
    explanations = list(result.get("explanations") or [""])
    explanations[0] = f"{explanations[0]}\n{note}" if explanations[0] else note
    entry = {"iteration": len(state.clusters) + 1, "node": node, "edit_mode": "rewrite_restore",
             "restored": restored}
    return {**result, "clusters": [clusters], "explanations": explanations,
            "status": list(result.get("status") or []) + [note], "operation_log": [entry]}
