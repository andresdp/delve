"""The tool loop of tool-based taxonomy updates (``taxonomy.edit_mode: tools``).

The generation LLM is bound to the editor's coding operations (``TOOL_SCHEMAS``)
and called in turns: each turn's tool calls are applied in order by the
``TaxonomyEditor``, and every call gets a reply (``ok: …`` or ``error: …``) so
the model can correct itself. The loop ends when the model calls ``finish``,
answers without tool calls, reaches ``max_steps`` turns, or a model call fails;
operations applied so far are always kept (the taxonomy is never re-emitted).
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from pydantic import BaseModel, Field

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


class AddValue(BaseModel):
    """Add a candidate decision or outcome to a dimension, citing the batch documents that support it."""

    dimension_id: str = Field(description="Id of the dimension (e.g. '3').")
    label: str = Field(description="Noun phrase naming the decision or outcome; never prefixed with the status.")
    description: str = Field(description="What this value means along its dimension.")
    status: DecisionStatus = Field(
        description="accepted: adopted; rejected: explicitly declined; outcome: an effect, not a decision.")
    doc_ids: List[str] = Field(description="Ids of documents in this batch whose codes support the value.")
    reason: str = Reason


class AddEvidence(BaseModel):
    """Cite batch documents as further evidence for an existing value (same option, same status)."""

    value_id: str = Field(description="Id of the value (e.g. '3.2').")
    doc_ids: List[str] = Field(description="Ids of documents in this batch that support it.")
    reason: str = Reason


class MoveValue(BaseModel):
    """Move a value to the dimension whose question it answers (it gets a new id there)."""

    value_id: str
    to_dimension_id: str
    reason: str = Reason


class MergeValues(BaseModel):
    """Merge values of one dimension and identical status that name the same option."""

    value_ids: List[str] = Field(description="Two or more value ids; the first one is kept.")
    label: str
    description: str
    reason: str = Reason


class RelabelValue(BaseModel):
    """Rewrite a value's label (and optionally its description)."""

    value_id: str
    label: str
    description: str | None = None
    reason: str = Reason


class SetStatus(BaseModel):
    """Reclassify a value's status on direct evidence (cite the document id in the reason)."""

    value_id: str
    status: DecisionStatus
    reason: str = Reason


class RemoveValue(BaseModel):
    """Remove a value with no supporting documents (supported values cannot be removed)."""

    value_id: str
    reason: str = Reason


class AddDimension(BaseModel):
    """Open a new dimension (decision point); add its values in the next turn, using the returned id."""

    name: str = Field(description="Noun phrase naming the axis of variation.")
    description: str = Field(description="The one question the dimension's values answer.")
    reason: str = Reason


class RenameDimension(BaseModel):
    """Rename a dimension and optionally rewrite its description."""

    dimension_id: str
    name: str
    description: str | None = None
    reason: str = Reason


class SplitPart(BaseModel):
    """One part of a split."""

    name: str
    description: str
    value_ids: List[str]


class SplitDimension(BaseModel):
    """Split a dimension that bundles several questions; every part keeps at least two candidate decisions."""

    dimension_id: str
    parts: List[SplitPart] = Field(description="Two or more parts; every value goes to exactly one part.")
    reason: str = Reason


class MergeDimensions(BaseModel):
    """Merge dimensions that ask the same question; the first id is kept."""

    dimension_ids: List[str]
    name: str
    description: str
    reason: str = Field(description="The shared question that makes these dimensions one decision point.")


class RemoveDimension(BaseModel):
    """Remove an empty dimension (move its values first)."""

    dimension_id: str
    reason: str = Reason


class AddRelation(BaseModel):
    """Relate two dimensions when the use case's logic requires it."""

    source_id: str
    target_id: str
    type: RelationType = Field(description=(
        "precondition: a choice on the target is required before the source applies; consequence: choices on "
        "the source imply outcomes on the target; co_occurring: both appear together, neither causes the other; "
        "constrains: the source restricts the target's available choices."))
    rationale: str


class RemoveRelation(BaseModel):
    """Remove the relations from one dimension to another."""

    source_id: str
    target_id: str
    reason: str = Reason


class Finish(BaseModel):
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
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {"type": "function", "function": {"name": name, "description": (model.__doc__ or "").strip(),
                                      "parameters": model.model_json_schema()}}
    for name, model in TOOLS
]


def _bind(model: Any, parallel: bool) -> Any:
    """Bind the tools; OpenAI chat models go through the Responses API.

    Newer OpenAI reasoning models (e.g. gpt-5.6-luna) reject function tools on Chat
    Completions when a reasoning effort is set; the Responses API accepts them.
    """
    if "use_responses_api" in getattr(type(model), "model_fields", {}):
        model = model.model_copy(update={"use_responses_api": True})
    return model.bind_tools(TOOL_SCHEMAS, parallel_tool_calls=True) if parallel else model.bind_tools(TOOL_SCHEMAS)


async def _invoke(model: Any, bound: Any, parallel: bool, messages: list, config: Any) -> tuple[Any, Any, bool, Any]:
    """Call the bound model once; on a parallel_tool_calls rejection rebind without it and retry once.

    Returns ``(ai_message or None, bound, parallel, error or None)``.
    """
    try:
        return await bound.ainvoke(messages, config=config), bound, parallel, None
    except Exception as exc:
        if not (parallel and "parallel_tool_calls" in str(exc)):
            return None, bound, parallel, exc
    logger.warning("Model rejects parallel_tool_calls; continuing with sequential tool calls")
    bound = _bind(model, parallel=False)
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


def _finish_reply(editor: TaxonomyEditor, args: Any, failed: int, reminded: bool) -> tuple[str, bool]:
    """Reply to a finish call: refused while calls of the turn failed, reminded once of uncited documents."""
    if editor.finished:
        return "ignored: the update already finished", reminded
    if failed:
        return (f"not finished: {failed} call{'s' if failed != 1 else ''} of this turn failed; fix "
                f"{'them' if failed != 1 else 'it'} (see the errors above), then call finish again"), reminded
    uncited = editor.uncited_now()
    if uncited and not reminded:
        return (f"not finished: batch documents {', '.join(uncited)} are cited by no value. Cite their codes with "
                "add_evidence or add_value, or call finish again if they are irrelevant to the use case"), True
    return editor.apply("finish", args if isinstance(args, dict) else {})[1], reminded


async def run_tool_update(model: Any, editor: TaxonomyEditor, messages: List[BaseMessage], max_steps: int,
                          config: Any = None) -> tuple[list[dict], str]:
    """Run the tool loop on ``editor``; return the edited taxonomy and the explanation.

    Within a turn, ``finish`` is handled after the other calls and honored only when
    none of them failed; the first ``finish`` with uncited batch documents gets one
    reminder. A turn without tool calls gets one nudge. ``editor.stop`` records why the
    loop ended (``STOP_TEXT`` keys).
    """
    messages = list(messages)
    parallel = True
    bound = _bind(model, parallel)
    stop, reminded, nudged = "step_limit", False, False
    for step in range(max_steps):
        ai, bound, parallel, error = await _invoke(model, bound, parallel, messages, config)
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
        failed = 0
        for tc in calls:
            if tc["name"] == "finish":
                continue
            ok, msg = editor.apply(tc["name"], tc.get("args") or {})
            failed += not ok
            messages.append(ToolMessage(msg, tool_call_id=tc["id"]))
        for bad in invalid:
            error = f"could not parse arguments: {bad.get('error') or 'invalid JSON'}"
            editor.log_rejected(bad.get("name") or "?", bad.get("args"), error)
            failed += 1
            if bad.get("id"):  # every tool call id needs a reply, or the next request fails
                messages.append(ToolMessage(f"error: {error}", tool_call_id=bad["id"]))
        for tc in calls:
            if tc["name"] == "finish":
                msg, reminded = _finish_reply(editor, tc.get("args"), failed, reminded)
                messages.append(ToolMessage(msg, tool_call_id=tc["id"]))
        if editor.finished:
            stop = "finish"
            break
    if stop == "step_limit":
        logger.warning("Tool update reached the step limit (%d turns); keeping %d applied operations",
                       max_steps, len(editor.operations))
    editor.stop = stop
    clusters = editor.result()
    explanation = editor.explanation if editor.finished else fallback_explanation(editor, stop)
    return clusters, explanation


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
    clusters, explanation = await run_tool_update(model, editor, messages,
                                                  max_steps=configuration.edit_max_steps or TaxonomySettings.edit_max_steps, config=config)
    entry = {"iteration": len(state.clusters) + 1, "node": node, "edit_mode": "tools", **editor.summary(),
             "explanation": explanation}
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
