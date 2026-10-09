"""Decision-focus passes after consolidation: merge sibling dimensions, rehome values.

The quality probe found that a fifth to a third of candidate values answer a different
question than their dimension, and that runs keep more, finer dimensions than the expert
models (plan ``docs/plans/2026-10-08-1500-feat-decision-focus-pass-plan.md``). Two passes
work on a finished (consolidated) taxonomy:

- **merge**: one structured LLM call over all dimensions proposes groups of dimensions that
  are parts of one design decision; each group is applied with ``merge_dimensions``.
- **rehome**: one structured LLM call per dimension, all on the same snapshot, proposes for
  each value ``keep``, ``move`` (to the dimension whose question it answers) or ``outcome``
  (a goal or principle, not an option); applied with ``move_value`` and ``set_status``.

Proposals are applied through ``TaxonomyEditor`` in review mode, which validates every
operation and records rejections, so a bad proposal never corrupts the taxonomy. A failed
LLM call leaves its dimension (or, for merge, the whole taxonomy) unchanged. The prompts
see the use case and the taxonomy only, never a ground truth. Evidence summaries are
recomputed afterwards, as evidence linking computes them.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Sequence, Tuple

from taxonomy_generator.nodes.evidence_linker import source_of
from taxonomy_generator.prompts import DECISION_FOCUS_MERGE_PROMPT, DECISION_FOCUS_REHOME_PROMPT
from taxonomy_generator.schemas import DimensionFocusOutput, SiblingMergeOutput
from taxonomy_generator.taxonomy_editor import TaxonomyEditor

logger = logging.getLogger(__name__)

PASSES = ("merge", "rehome")
# Value labels shown per dimension in the merge call (enough to judge the axis).
MAX_LABELS = 15


def _new_log() -> Dict[str, list]:
    return {"applied": [], "rejected": [], "failed_calls": []}


def _apply(editor: TaxonomyEditor, log: Dict[str, list], name: str, args: dict) -> None:
    ok, message = editor.apply(name, args)
    (log["applied"] if ok else log["rejected"]).append({"tool": name, "args": args, "message": message})


def _dimension_summary(cluster: dict, with_values: bool) -> dict:
    out = {"id": str(cluster.get("id")), "name": cluster.get("name", ""), "description": cluster.get("description", "")}
    if with_values:
        out["values"] = [v.get("label", "") for v in cluster.get("values") or []][:MAX_LABELS]
    return out


def recompute_evidence(clusters: List[dict]) -> List[dict]:
    """Recompute each dimension's evidence summary from its values (codes, documents, sources)."""
    for cluster in clusters:
        values = [v for v in cluster.get("values") or [] if isinstance(v, dict)]
        docs = {str(d) for v in values for d in v.get("supporting_doc_ids") or []}
        cluster["evidence"] = {
            "codes": sum(int(v.get("evidence_code_count") or 0) for v in values),
            "documents": len(docs),
            "sources": len({source_of(d) for d in docs}),
        }
    return clusters


async def merge_siblings(clusters: List[dict], model: Any, use_case: str) -> Tuple[List[dict], Dict[str, list]]:
    """Merge groups of dimensions that are parts of one design decision. Returns ``(clusters, log)``."""
    log = _new_log()
    payload = json.dumps([_dimension_summary(c, True) for c in clusters], ensure_ascii=False, indent=1)
    try:
        messages = DECISION_FOCUS_MERGE_PROMPT.format_messages(use_case=use_case, dimensions_json=payload)
        proposal = await model.with_structured_output(SiblingMergeOutput).ainvoke(messages)
    except Exception as exc:  # noqa: BLE001 — a failed call keeps the taxonomy unchanged
        logger.warning("Decision-focus merge call failed: %s", exc)
        log["failed_calls"].append({"pass": "merge", "error": f"{type(exc).__name__}: {exc}"})
        return clusters, log
    editor = TaxonomyEditor(clusters, batch_doc_ids=[], review=True)
    for group in proposal.groups:
        _apply(editor, log, "merge_dimensions", {"dimension_ids": list(group.dimension_ids), "name": group.name,
                                                 "description": group.description,
                                                 "reason": f"{group.question} {group.reason}".strip()})
    return editor.result(), log


async def rehome_values(clusters: List[dict], model: Any, use_case: str,
                        concurrency: int = 5) -> Tuple[List[dict], Dict[str, list]]:
    """Move values to the dimension whose question they answer; turn goals into outcomes."""
    log = _new_log()
    structured = model.with_structured_output(DimensionFocusOutput)
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def propose(cluster: dict):
        others = [_dimension_summary(c, False) for c in clusters if c is not cluster]
        under_review = {**_dimension_summary(cluster, False),
                        "values": [{"id": str(v.get("id")), "label": v.get("label", ""),
                                    "description": v.get("description", ""), "status": v.get("status", "")}
                                   for v in cluster.get("values") or []]}
        async with semaphore:
            try:
                messages = DECISION_FOCUS_REHOME_PROMPT.format_messages(
                    use_case=use_case, dimension_json=json.dumps(under_review, ensure_ascii=False, indent=1),
                    other_dimensions_json=json.dumps(others, ensure_ascii=False, indent=1))
                return cluster, await structured.ainvoke(messages)
            except Exception as exc:  # noqa: BLE001 — a failed call keeps this dimension unchanged
                logger.warning("Decision-focus rehome call failed for dimension %s: %s", cluster.get("id"), exc)
                log["failed_calls"].append({"pass": "rehome", "dimension_id": str(cluster.get("id")),
                                            "error": f"{type(exc).__name__}: {exc}"})
                return cluster, None

    proposals = await asyncio.gather(*(propose(c) for c in clusters))
    editor = TaxonomyEditor(clusters, batch_doc_ids=[], review=True)
    for cluster, proposal in proposals:
        if proposal is None:
            continue
        own = {str(v.get("id")) for v in cluster.get("values") or []}
        for item in proposal.values:
            if item.action == "keep":
                continue
            if item.value_id not in own:
                log["rejected"].append({"tool": item.action, "args": item.model_dump(),
                                        "message": f"value {item.value_id} is not in dimension {cluster.get('id')}"})
                continue
            if item.action == "move":
                _apply(editor, log, "move_value", {"value_id": item.value_id, "to_dimension_id": item.to_dimension_id,
                                                   "reason": item.reason})
            else:
                _apply(editor, log, "set_status", {"value_id": item.value_id, "status": "outcome",
                                                   "reason": item.reason})
    return editor.result(), log


async def apply_passes(clusters: List[dict], model: Any, use_case: str,
                       passes: Sequence[str]) -> Tuple[List[dict], List[dict]]:
    """Run the named passes in order and recompute evidence. Returns ``(clusters, focus log)``."""
    unknown = [p for p in passes if p not in PASSES]
    if unknown:
        raise ValueError(f"unknown decision-focus pass(es) {unknown}; known: {', '.join(PASSES)}")
    focus_log = []
    for name in passes:
        run = merge_siblings if name == "merge" else rehome_values
        clusters, log = await run(clusters, model, use_case)
        focus_log.append({"pass": name, **log})
    return recompute_evidence(clusters), focus_log
