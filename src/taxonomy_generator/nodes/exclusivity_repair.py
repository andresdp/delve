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
from taxonomy_generator.taxonomy_editor import EditError, TaxonomyEditor

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
    before = taxonomy_exclusivity(clusters, min_units=min_units)
    dims_before = len(clusters)
    targets = [r for r in before["dimensions"] if r["score"] is not None and r["score"] < min_score
               and r["units"] >= min_units and r["pairs"]]
    log: Dict[str, Any] = {"node": "exclusivity_repair", "before": before["score"], "after": before["score"],
                           "dimensions_before": dims_before, "dimensions_after": dims_before,
                           "dimensions": [r["id"] for r in targets], "operations": [], "rejected": [],
                           "failed_calls": [], "rationales": {}}
    if not targets:
        return clusters, log

    structured = model.with_structured_output(ExclusivityRepairOutput)
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def propose(row: Mapping[str, Any], current: List[dict], retry_note: str):
        dim = next(c for c in current if str(c.get("id")) == row["id"])
        async with semaphore:
            try:
                messages = EXCLUSIVITY_REPAIR_PROMPT.format_messages(
                    use_case=use_case, retry_note=retry_note, **_payload(dim, row, current, passages))
                return row["id"], await structured.ainvoke(messages)
            except Exception as exc:  # noqa: BLE001 — a failed call keeps this dimension unchanged
                logger.warning("Exclusivity repair call failed for dimension %s: %s", row["id"], exc)
                log["failed_calls"].append({"dimension_id": row["id"], "error": f"{type(exc).__name__}: {exc}"})
                return row["id"], None

    # Round 1 on every target; round 2 only on dimensions whose proposals were rejected, with the errors.
    notes: Dict[str, str] = {}
    for round_no in (1, 2):
        if round_no == 2:
            rows = {r["id"]: r for r in taxonomy_exclusivity(clusters)["dimensions"]}
            targets = [rows[d] for d in notes if d in rows and rows[d]["pairs"]]
            if not targets:
                break
        answers = await asyncio.gather(*(propose(r, clusters, notes.get(r["id"], "")) for r in targets))
        proposals = [(d, p) for d, p in answers if p is not None]
        for dim_id, proposal in proposals:
            log["rationales"][dim_id if round_no == 1 else f"{dim_id} (retry)"] = proposal.rationale
        clusters, notes = _apply_round(clusters, proposals, log, round_no, relation_types, max_relations)
        if not notes:
            break

    clusters = recompute_evidence(clusters)
    log["after"] = taxonomy_exclusivity(clusters, min_units=min_units)["score"]
    log["dimensions_after"] = len(clusters)
    return clusters, log


RETRY_NOTE = ("## Your previous proposal\n\nThese actions for this dimension were rejected:\n\n{errors}\n\n"
              "Propose corrected actions. Every split part needs at least two candidate decisions, and so does an "
              "extracted dimension: move a lone value to the existing dimension whose question it answers, or make "
              "it an outcome if it is a goal or an effect rather than an option.")


def _apply_round(clusters: List[dict], proposals: Sequence[Tuple[str, ExclusivityRepairOutput]], log: Dict[str, Any],
                 round_no: int, relation_types: Sequence[str],
                 max_relations: Optional[int]) -> Tuple[List[dict], Dict[str, str]]:
    """Apply one round of proposals; return the clusters and, per dimension, a note on its rejected actions."""
    rejected: Dict[str, List[str]] = {}

    def record(ok: bool, dim_id: str, action: ExclusivityAction, message: str) -> None:
        entry = {"dimension_id": dim_id, "action": action.action, "reason": action.reason, "message": message,
                 "round": round_no}
        (log["operations"] if ok else log["rejected"]).append(entry)
        if not ok:
            rejected.setdefault(dim_id, []).append(f"- {action.action} {', '.join(action.value_ids)}: {message}")

    by_id = {str(c.get("id")): c for c in clusters}
    # 1. merges, directly (the editor merges neither stances nor values of different status)
    aliases: Dict[str, str] = {}
    for dim_id, proposal in proposals:
        for action in proposal.actions:
            if action.action == "merge":
                try:
                    record(True, dim_id, action, merge_candidates(by_id[dim_id], action.value_ids, action.name,
                                                                  action.description))
                    for other in action.value_ids[1:]:
                        aliases[str(other)] = str(action.value_ids[0])
                except (ValueError, KeyError) as exc:
                    record(False, dim_id, action, str(exc))

    # 2. moves, outcomes, splits and extractions, through the editor (validated, atomic per operation)
    types = tuple(dict.fromkeys(list(relation_types) + ["refines"]))
    editor = TaxonomyEditor(clusters, batch_doc_ids=[], review=True, max_dimensions=None,
                            relation_types=types, max_relations=max_relations)
    resolve = lambda vid: editor.resolve_value(aliases.get(str(vid), str(vid)))  # noqa: E731
    order = {"move": 0, "outcome": 0, "split": 1, "extract": 1}  # values leave first, then the dimension is split
    actions = sorted(((d, a) for d, p in proposals for a in p.actions if a.action in order),
                     key=lambda x: order[x[1].action])
    for dim_id, action in actions:
        if action.action in ("move", "outcome"):
            problem = _leaves_one_candidate(editor, [resolve(v) for v in action.value_ids])
            if problem:
                record(False, dim_id, action, problem)
                continue
        if action.action == "move":
            for vid in action.value_ids:
                ok, message = editor.apply("move_value", {"value_id": resolve(vid),
                                                          "to_dimension_id": action.to_dimension_id,
                                                          "reason": action.reason})
                record(ok, dim_id, action, message)
        elif action.action == "outcome":
            for vid in action.value_ids:
                ok, message = editor.apply("set_status", {"value_id": resolve(vid), "status": "outcome",
                                                          "reason": action.reason})
                record(ok, dim_id, action, message)
        elif action.action == "split":
            parts = [{"name": p.name, "description": p.description,
                      "value_ids": [resolve(v) for v in p.value_ids]} for p in action.parts]
            ok, message = editor.apply("split_dimension", {"dimension_id": dim_id, "parts": parts})
            record(ok, dim_id, action, message)
        else:
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
    return result, {d: RETRY_NOTE.format(errors="\n".join(e)) for d, e in rejected.items()}


def _leaves_one_candidate(editor: TaxonomyEditor, value_ids: List[str]) -> str:
    """Why taking ``value_ids`` out would leave a dimension with one candidate decision ("" when it would not).

    Selection drops a dimension with a single candidate decision, so its last value would be lost: move it
    too (emptying the dimension) or keep the values where they are.
    """
    leaving: Dict[str, set] = {}
    for vid in value_ids:
        try:
            dim, _value = editor._value(vid)  # noqa: SLF001
        except EditError:  # an unknown id: the operation itself reports it
            return ""
        leaving.setdefault(str(dim["id"]), set()).add(str(vid))
    for did, ids in leaving.items():
        dim = editor._dim(did)  # noqa: SLF001
        left = [v for v in dim["values"] if str(v.get("id")) not in ids
                and v.get("status", "accepted") in CANDIDATE_STATUSES]
        if len(left) == 1:
            return (f"dimension {did} '{dim.get('name', '')}' would keep one candidate decision "
                    f"({left[0].get('id')} '{left[0].get('label', '')}'), and a dimension with one candidate is dropped "
                    "with its value: move that value as well, or keep the values where they are")
    return ""


def _extract(editor: TaxonomyEditor, dim_id: str, value_ids: List[str], action: ExclusivityAction) -> Tuple[bool, str]:
    """Move ``value_ids`` to a new dimension that refines ``dim_id``; undone when any step fails."""
    snapshot = editor._snapshot()  # noqa: SLF001 — the extraction is one operation for the log
    applied = len(editor.operations)
    if not value_ids:
        return False, "extract needs value_ids"
    try:
        candidates = sum(editor._value(v)[1].get("status", "accepted") in CANDIDATE_STATUSES  # noqa: SLF001
                         for v in value_ids)
    except Exception as exc:  # noqa: BLE001 — an unknown value id
        return False, str(exc)
    if candidates < 2:
        return False, (f"the new dimension would keep {candidates} candidate decision(s); a decision point needs at "
                       "least 2. Move a lone value to the existing dimension whose question it answers instead")
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
