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
from typing import Any, List, Literal

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from pydantic import BaseModel, Field

from taxonomy_generator.taxonomy_editor import RELATION_TYPES, TaxonomyEditor

logger = logging.getLogger(__name__)

Reason = Field(description="Short justification of this change: the new data or feedback issue behind it.")


class AddValue(BaseModel):
    """Add a candidate decision or outcome to a dimension, citing the batch documents that support it."""

    dimension_id: str = Field(description="Id of the dimension (e.g. '3').")
    label: str = Field(description="Noun phrase naming the decision or outcome; never prefixed with the status.")
    description: str = Field(description="What this value means along its dimension.")
    status: Literal["accepted", "rejected", "outcome"] = Field(
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
    status: Literal["accepted", "rejected", "outcome"]
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
    type: Literal[RELATION_TYPES] = Field(description="precondition, consequence, co_occurring or constrains.")  # type: ignore[valid-type]
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
    return model.bind_tools(TOOL_SCHEMAS, parallel_tool_calls=True) if parallel else model.bind_tools(TOOL_SCHEMAS)


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
    return f"{text}. The update ended without finish: {stop}."


async def run_tool_update(model: Any, editor: TaxonomyEditor, messages: List[BaseMessage], max_steps: int = 8,
                          config: Any = None) -> tuple[list[dict], str]:
    """Run the tool loop on ``editor``; return the edited taxonomy and the explanation."""
    messages = list(messages)
    parallel = True
    bound = _bind(model, parallel)
    stop = f"step limit ({max_steps} turns) reached"
    for step in range(max_steps):
        try:
            ai = await bound.ainvoke(messages, config=config)
        except Exception as exc:
            if parallel and "parallel_tool_calls" in str(exc):
                logger.warning("Model rejects parallel_tool_calls; continuing with sequential tool calls")
                parallel = False
                bound = _bind(model, parallel)
                try:
                    ai = await bound.ainvoke(messages, config=config)
                except Exception as retry_exc:
                    exc = retry_exc
                    ai = None
            else:
                ai = None
            if ai is None:
                logger.warning("Tool update: model call failed at turn %d (%s: %s); keeping %d applied operations",
                               step + 1, type(exc).__name__, exc, len(editor.operations))
                stop = f"model call failed ({type(exc).__name__})"
                break
        if not isinstance(ai, AIMessage):
            ai = AIMessage(content=str(getattr(ai, "content", ai)))
        messages.append(ai)
        calls, invalid = ai.tool_calls or [], ai.invalid_tool_calls or []
        if not calls and not invalid:
            stop = "the model made no tool call"
            break
        for tc in calls:
            if editor.finished:
                msg = "ignored: the update already finished"
            else:
                _ok, msg = editor.apply(tc["name"], tc.get("args") or {})
            messages.append(ToolMessage(msg, tool_call_id=tc["id"]))
        for bad in invalid:  # every tool call id needs a reply, or the next request fails
            error = f"could not parse arguments: {bad.get('error') or 'invalid JSON'}"
            editor.log_rejected(bad.get("name") or "?", bad.get("args"), error)
            messages.append(ToolMessage(f"error: {error}", tool_call_id=bad.get("id") or ""))
        if editor.finished:
            break
    else:
        logger.warning("Tool update reached the step limit (%d turns); keeping %d applied operations",
                       max_steps, len(editor.operations))
    clusters = editor.result()
    explanation = editor.explanation if editor.finished else fallback_explanation(editor, stop)
    return clusters, explanation
