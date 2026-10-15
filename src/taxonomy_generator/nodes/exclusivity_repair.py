"""Exclusivity repair: fix dimensions whose sources adopt several of their values.

A system should adopt one value per dimension (``evaluation/exclusivity.py``). After evidence
linking, every dimension whose exclusivity is below ``taxonomy.exclusivity_min`` (with at least
``exclusivity_min_units`` adopting sources) gets one structured LLM call. The call sees the
use case, the dimension, the pairs of values adopted together with short passage excerpts, and
the other dimensions, and proposes (plan ``docs/plans/2026-10-15-feat-value-exclusivity-plan.md``):

- ``split``: the dimension bundles several decisions (``TaxonomyEditor.split_dimension``);
- ``extract``: values answering a sub-question become a new dimension that ``refines`` this one;
- ``merge``: values that are one option (stances and evidence are unioned, as consolidation does);
- ``hybrid``: values systems deliberately combine, recorded on the dimension as ``hybrids``.

Proposals go through ``TaxonomyEditor`` in review mode, so an invalid one is rejected and logged
and never corrupts the taxonomy; a failed call leaves its dimension unchanged. Exclusivity is
not enforced beyond that: what the repair leaves is reported (and penalized on the scoreboard).
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from taxonomy_generator.evaluation.exclusivity import taxonomy_exclusivity
from taxonomy_generator.nodes.decision_focus import recompute_evidence
from taxonomy_generator.nodes.evidence_linker import CANDIDATE_STATUSES, initial_stances, status_from_stances
from taxonomy_generator.prompts import EXCLUSIVITY_REPAIR_PROMPT
from taxonomy_generator.schemas import ExclusivityAction, ExclusivityRepairOutput
from taxonomy_generator.taxonomy_editor import TaxonomyEditor

logger = logging.getLogger(__name__)

MAX_PAIRS = 8          # value pairs shown per dimension
MAX_EXCERPTS = 3       # passage excerpts per pair
EXCERPT_WORDS = 45


def _excerpt(text: str, words: int = EXCERPT_WORDS) -> str:
    parts = str(text or "").split()
    return " ".join(parts[:words]) + (" ..." if len(parts) > words else "")


def _payload(dim: Mapping[str, Any], row: Mapping[str, Any], clusters: Sequence[Mapping[str, Any]],
             passages: Mapping[str, str]) -> Dict[str, str]:
    dimension = {"id": str(dim.get("id")), "name": dim.get("name", ""), "description": dim.get("description", ""),
                 "values": [{"id": str(v.get("id")), "label": v.get("label", ""), "description": v.get("description", ""),
                             "status": v.get("status", "")} for v in dim.get("values") or []]}
    pairs = [{"values": [{"id": i, "label": label} for i, label in zip(p["values"], p["labels"])],
              "sources": p["units"],
              "excerpts": [{"passage": d, "text": _excerpt(passages[d])} for d in p["docs"] if d in passages][:MAX_EXCERPTS]}
             for p in row["pairs"][:MAX_PAIRS]]
    others = [{"id": str(c.get("id")), "name": c.get("name", ""), "description": c.get("description", "")}
              for c in clusters if c is not dim]
    dump = lambda x: json.dumps(x, ensure_ascii=False, indent=1)  # noqa: E731
    return {"dimension_json": dump(dimension), "pairs_json": dump(pairs), "other_dimensions_json": dump(others)}


def merge_candidates(dim: dict, value_ids: Sequence[str], label: str, description: str) -> str:
    """Merge candidate values of one dimension into the first: evidence, stances and provenance are unioned.

    Raises ``ValueError`` when a value is missing, repeated or not a candidate decision.
    """
    by_id = {str(v.get("id")): v for v in dim.get("values") or []}
    ids = [str(i) for i in value_ids]
    if len(ids) < 2 or len(set(ids)) < len(ids):
        raise ValueError("merge needs at least two different values")
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise ValueError(f"value(s) {', '.join(missing)} not in dimension {dim.get('id')}")
    found = [by_id[i] for i in ids]
    if any(v.get("status", "accepted") not in CANDIDATE_STATUSES for v in found):
        raise ValueError("merge applies to candidate decisions only, not outcomes")
    keep, others = found[0], found[1:]
    stances: Dict[str, List[str]] = {}
    for v in found:
        for stance, docs in initial_stances(v).items():
            stances.setdefault(stance, []).extend(docs)
    keep["stances"] = {k: sorted(set(v)) for k, v in stances.items() if v}
    keep["status"] = status_from_stances(keep["stances"], keep.get("status", "accepted"))
    keep["supporting_doc_ids"] = sorted({str(d) for v in found for d in v.get("supporting_doc_ids") or []})
    keep["evidence_code_count"] = sum(int(v.get("evidence_code_count") or 0) for v in found)
    keep["merged_from"] = list(keep.get("merged_from") or []) + [
        {"id": v.get("id"), "label": v.get("label", "")} for v in others]
    if label.strip():
        keep["label"] = label.strip()
    if description.strip():
        keep["description"] = description.strip()
    dim["values"] = [v for v in dim["values"] if v not in others]
    return f"merged {', '.join(ids[1:])} into {ids[0]} '{keep.get('label', '')}' in dimension {dim.get('id')}"


async def repair_exclusivity(
    clusters: List[dict],
    model: Any,
    use_case: str,
    passages: Mapping[str, str],
    min_score: float = 0.8,
    min_units: int = 2,
    relation_types: Sequence[str] = (),
    max_relations: Optional[int] = None,
    concurrency: int = 5,
) -> Tuple[List[dict], Dict[str, Any]]:
    """Repair the dimensions with low exclusivity. Returns ``(clusters, log)``; the input is not modified.

    The log holds the exclusivity before and after, the dimensions sent, the applied and
    rejected operations, the failed calls and each call's rationale.
    """
    clusters = copy.deepcopy([c for c in clusters if isinstance(c, dict)])
    before = taxonomy_exclusivity(clusters)
    targets = [r for r in before["dimensions"] if r["score"] is not None and r["score"] < min_score
               and r["units"] >= min_units and r["pairs"]]
    log: Dict[str, Any] = {"node": "exclusivity_repair", "before": before["score"], "after": before["score"],
                           "dimensions": [r["id"] for r in targets], "operations": [], "rejected": [],
                           "failed_calls": [], "rationales": {}}
    if not targets:
        return clusters, log

    by_id = {str(c.get("id")): c for c in clusters}
    structured = model.with_structured_output(ExclusivityRepairOutput)
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def propose(row: Mapping[str, Any]):
        dim = by_id[row["id"]]
        async with semaphore:
            try:
                messages = EXCLUSIVITY_REPAIR_PROMPT.format_messages(use_case=use_case,
                                                                     **_payload(dim, row, clusters, passages))
                return row["id"], await structured.ainvoke(messages)
            except Exception as exc:  # noqa: BLE001 — a failed call keeps this dimension unchanged
                logger.warning("Exclusivity repair call failed for dimension %s: %s", row["id"], exc)
                log["failed_calls"].append({"dimension_id": row["id"], "error": f"{type(exc).__name__}: {exc}"})
                return row["id"], None

    proposals = [(d, p) for d, p in await asyncio.gather(*(propose(r) for r in targets)) if p is not None]

    def record(ok: bool, dim_id: str, action: ExclusivityAction, message: str) -> None:
        entry = {"dimension_id": dim_id, "action": action.action, "reason": action.reason, "message": message}
        (log["operations"] if ok else log["rejected"]).append(entry)

    # 1. merges, directly (the editor merges neither stances nor values of different status)
    aliases: Dict[str, str] = {}
    for dim_id, proposal in proposals:
        log["rationales"][dim_id] = proposal.rationale
        for action in proposal.actions:
            if action.action == "merge":
                try:
                    record(True, dim_id, action, merge_candidates(by_id[dim_id], action.value_ids, action.name,
                                                                  action.description))
                    for other in action.value_ids[1:]:
                        aliases[str(other)] = str(action.value_ids[0])
                except ValueError as exc:
                    record(False, dim_id, action, str(exc))

    # 2. splits and extractions, through the editor (validated, atomic per operation)
    types = tuple(dict.fromkeys(list(relation_types) + ["refines"]))
    editor = TaxonomyEditor(clusters, batch_doc_ids=[], review=True, max_dimensions=None,
                            relation_types=types, max_relations=max_relations)
    resolve = lambda vid: editor.resolve_value(aliases.get(str(vid), str(vid)))  # noqa: E731
    for dim_id, proposal in proposals:
        for action in proposal.actions:
            if action.action == "split":
                parts = [{"name": p.name, "description": p.description,
                          "value_ids": [resolve(v) for v in p.value_ids]} for p in action.parts]
                ok, message = editor.apply("split_dimension", {"dimension_id": dim_id, "parts": parts})
                record(ok, dim_id, action, message)
            elif action.action == "extract":
                ok, message = _extract(editor, dim_id, [resolve(v) for v in action.value_ids], action)
                record(ok, dim_id, action, message)
    result = editor.result()

    # 3. hybrids, on the dimension that holds every value afterwards
    for dim_id, proposal in proposals:
        for action in proposal.actions:
            if action.action != "hybrid":
                continue
            ids = list(dict.fromkeys(resolve(v) for v in action.value_ids))
            home = [c for c in result if ids and all(i in {str(v.get("id")) for v in c.get("values") or []} for i in ids)]
            if len(ids) < 2 or not home:
                record(False, dim_id, action, "a hybrid needs at least two values of one dimension")
                continue
            home[0].setdefault("hybrids", []).append({"value_ids": ids, "reason": action.reason})
            record(True, dim_id, action, f"declared hybrid {', '.join(ids)} in dimension {home[0].get('id')}")

    result = recompute_evidence(result)
    log["after"] = taxonomy_exclusivity(result)["score"]
    return result, log


def _extract(editor: TaxonomyEditor, dim_id: str, value_ids: List[str], action: ExclusivityAction) -> Tuple[bool, str]:
    """Move ``value_ids`` to a new dimension that refines ``dim_id``; undone when any step fails."""
    snapshot = editor._snapshot()  # noqa: SLF001 — the extraction is one operation for the log
    applied = len(editor.operations)
    if not value_ids:
        return False, "extract needs value_ids"
    ok, message = editor.apply("add_dimension", {"name": action.name, "description": action.description})
    if ok:
        new_id = str(editor.clusters[-1]["id"])
        for vid in value_ids:
            ok, message = editor.apply("move_value", {"value_id": vid, "to_dimension_id": new_id,
                                                      "reason": action.reason})
            if not ok:
                break
        if ok:
            parent = editor._dim(dim_id).get("name", dim_id)  # noqa: SLF001
            ok, message = editor.apply("add_relation", {"source_id": new_id, "target_id": dim_id, "type": "refines",
                                                        "reading": f"{action.name} is a sub-decision of {parent}",
                                                        "rationale": action.reason})
    if not ok:
        editor._restore(snapshot)  # noqa: SLF001
        del editor.operations[applied:]
        return False, message
    return True, f"extracted {', '.join(value_ids)} from dimension {dim_id} into {new_id} '{action.name}' (refines {dim_id})"
