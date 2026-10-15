"""Value recoding: redefine a dimension's values as exclusive alternatives.

A system should take one value per dimension. When sources adopt several values of one dimension, the
values often describe parts or degrees of an approach rather than alternatives (plan
``docs/plans/2026-10-15-feat-value-recoding-plan.md``, cause i). This step rewrites such values as
alternative answers and assigns every observed **combination** (the set of values one source adopts) to
exactly one of them; the old values are kept inside the new ones as facets (``includes``).

1. **Select** (deterministic): exclusivity below ``recoding_min_exclusivity``, at least
   ``recoding_min_sources`` adopting sources, and at least ``recoding_min_recurring`` of them on a
   combination another source shares. Dimensions failing only the last test are logged as **likely
   cause (ii)**: the dimension itself groups several concerns.
2. **Propose**: one structured LLM call per dimension (values, assignments, or ``keep``).
3. **Validate** (deterministic): at least two new values and no more than the old ones; every old value
   included; every combination assigned once, to a value that includes all of it; every new value
   adopted by at least ``min_sources_per_value`` sources (no per-source bundles). One retry with the errors.
4. **Apply**: new values with ``includes``, evidence from the assigned sources' passages, stances and
   status recomputed; values no source adopts (only rejections) and outcomes stay as they are.
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

from taxonomy_generator.evaluation.exclusivity import (
    adopting_docs,
    value_combinations,
    dimension_exclusivity,
    generality,
    recurring_share,
    taxonomy_exclusivity,
)
from taxonomy_generator.nodes.decision_focus import recompute_evidence
from taxonomy_generator.nodes.evidence_linker import CANDIDATE_STATUSES, source_of, status_from_stances
from taxonomy_generator.prompts import VALUE_RECODING_PROMPT
from taxonomy_generator.schemas import RecodingOutput

logger = logging.getLogger(__name__)

MAX_EXCERPTS = 2
EXCERPT_WORDS = 40
RETRY_NOTE = ("## Your previous proposal\n\nIt was rejected:\n\n{errors}\n\nPropose a corrected recoding, or set "
              "keep to true.")


def _excerpt(text: str) -> str:
    words = str(text or "").split()
    return " ".join(words[:EXCERPT_WORDS]) + (" ..." if len(words) > EXCERPT_WORDS else "")


def adoptable(dim: Mapping[str, Any]) -> List[dict]:
    """The candidate values some source adopts: the ones recoding rewrites."""
    return [v for v in dim.get("values") or [] if isinstance(v, dict)
            and v.get("status", "accepted") in CANDIDATE_STATUSES and adopting_docs(v)]


def _combo_keys(dim: Mapping[str, Any]) -> Dict[str, Tuple[frozenset, List[str]]]:
    combos = sorted(value_combinations(dim).items(), key=lambda kv: (-len(kv[1]), sorted(kv[0])))
    return {f"C{i}": (vids, units) for i, (vids, units) in enumerate(combos, start=1)}


def _payload(dim: Mapping[str, Any], passages: Mapping[str, str]) -> Dict[str, str]:
    values = adoptable(dim)
    by_id = {str(v["id"]): v for v in values}
    docs_by_unit: Dict[str, List[str]] = {}
    for v in values:
        for doc in adopting_docs(v):
            docs_by_unit.setdefault(source_of(doc), []).append(doc)
    combos = []
    for key, (vids, units) in _combo_keys(dim).items():
        docs = [d for u in units for d in dict.fromkeys(docs_by_unit.get(u, []))]
        combos.append({"key": key, "values": [{"id": i, "label": by_id[i].get("label", "")} for i in sorted(vids)],
                       "sources": units,
                       "excerpts": [{"passage": d, "text": _excerpt(passages[d])} for d in docs if d in passages][:MAX_EXCERPTS]})
    dimension = {"id": str(dim.get("id")), "name": dim.get("name", ""), "question": dim.get("description", ""),
                 "values": [{"id": str(v["id"]), "label": v.get("label", ""), "description": v.get("description", "")}
                            for v in values]}
    dump = lambda x: json.dumps(x, ensure_ascii=False, indent=1)  # noqa: E731
    return {"dimension_json": dump(dimension), "combinations_json": dump(combos)}


def validate(dim: Mapping[str, Any], proposal: RecodingOutput, min_sources_per_value: int = 2) -> List[str]:
    """Problems that make a recoding unusable (empty when it can be applied)."""
    if proposal.keep:
        return []
    old = {str(v["id"]) for v in adoptable(dim)}
    combos = _combo_keys(dim)
    problems = []
    keys = [v.key for v in proposal.values]
    if len(set(keys)) < len(keys):
        problems.append("new value keys repeat")
    if len(keys) < 2:
        problems.append("a recoding needs at least two new values")
    if len(keys) > len(old):
        problems.append(f"{len(keys)} new values for {len(old)} current ones: use fewer, more general alternatives")
    includes = {v.key: {str(i) for i in v.includes} for v in proposal.values}
    unknown = sorted({i for inc in includes.values() for i in inc} - old)
    if unknown:
        problems.append(f"includes unknown values: {', '.join(unknown)}")
    missing = sorted(old - {i for inc in includes.values() for i in inc})
    if missing:
        problems.append(f"current values included in no new value: {', '.join(missing)}")
    assigned: Dict[str, List[str]] = {}
    for a in proposal.assignments:
        assigned.setdefault(a.combination, []).append(a.value_key)
    for key, (vids, _units) in combos.items():
        targets = assigned.get(key, [])
        if len(targets) != 1:
            problems.append(f"combination {key} must be assigned to exactly one new value (got {len(targets)})")
        elif targets[0] not in includes:
            problems.append(f"combination {key} is assigned to unknown value {targets[0]}")
        elif not vids <= includes[targets[0]]:
            problems.append(f"combination {key} is assigned to {targets[0]}, which does not include "
                            f"{', '.join(sorted(vids - includes[targets[0]]))}")
    extra = sorted(set(assigned) - set(combos))
    if extra:
        problems.append(f"unknown combinations: {', '.join(extra)}")
    if not problems:
        for v in proposal.values:
            n = sum(len(combos[c][1]) for c, ts in assigned.items() if ts == [v.key])
            if n < min_sources_per_value:
                problems.append(f"new value {v.key} '{v.label}' is adopted by {n} source(s); each needs at least "
                                f"{min_sources_per_value}: merge it with another alternative")
    return problems


def apply(dim: dict, proposal: RecodingOutput) -> Dict[str, Any]:
    """Rewrite ``dim``'s adopted values as the proposal's alternatives (validated first). Returns the fit record."""
    values = adoptable(dim)
    by_id = {str(v["id"]): v for v in values}
    combos = _combo_keys(dim)
    units_by_key: Dict[str, Set[str]] = {}
    for a in proposal.assignments:
        units_by_key.setdefault(a.value_key, set()).update(combos[a.combination][1])
    exact = sum(len(combos[a.combination][1]) for a in proposal.assignments
                if combos[a.combination][0] == {str(i) for i in next(v for v in proposal.values
                                                                        if v.key == a.value_key).includes})
    new_values = []
    for i, nv in enumerate(proposal.values, start=1):
        units = units_by_key.get(nv.key, set())
        olds = [by_id[str(x)] for x in nv.includes if str(x) in by_id]
        accepted = sorted({d for v in olds for d in adopting_docs(v) if source_of(d) in units})
        rejected = sorted({d for v in olds for d in (v.get("stances") or {}).get("rejected") or []} - set(accepted))
        stances = {k: d for k, d in (("accepted", accepted), ("rejected", rejected)) if d}
        new_values.append({
            "id": f"{dim.get('id')}.{i}", "dimension_id": str(dim.get("id")), "label": nv.label.strip(),
            "description": nv.description.strip(), "status": status_from_stances(stances, "accepted"),
            "stances": stances, "supporting_doc_ids": sorted(set(accepted) | set(rejected)),
            "evidence_code_count": sum(int(v.get("evidence_code_count") or 0) for v in olds),
            "includes": [{"id": str(v["id"]), "label": v.get("label", ""), "description": v.get("description", "")}
                         for v in olds],
        })
    rest = [v for v in dim.get("values") or [] if isinstance(v, dict) and str(v.get("id")) not in by_id]
    for j, v in enumerate(rest, start=len(new_values) + 1):
        v["id"] = f"{dim.get('id')}.{j}"
    dim["values"] = new_values + rest
    dim.pop("hybrids", None)  # hybrids named old value ids
    total = sum(len(u) for _vids, u in combos.values())
    return {"sources": total, "fit": exact / total if total else None}


async def recode_values(
    clusters: List[dict],
    model: Any,
    use_case: str,
    passages: Mapping[str, str],
    min_exclusivity: float = 0.8,
    min_sources: int = 3,
    min_recurring: float = 0.3,
    min_sources_per_value: int = 2,
    concurrency: int = 5,
) -> Tuple[List[dict], Dict[str, Any]]:
    """Recode the eligible dimensions. Returns ``(clusters, log)``; the input is not modified."""
    clusters = copy.deepcopy([c for c in clusters if isinstance(c, dict)])
    selected, cause_ii = [], []
    for c in clusters:
        row = dimension_exclusivity(c)
        if row["score"] is None or row["score"] >= min_exclusivity or row["units"] < min_sources:
            continue
        share = recurring_share(c)
        (selected if share >= min_recurring else cause_ii).append(
            {"id": str(c.get("id")), "name": c.get("name", ""), "exclusivity": round(row["score"], 3),
             "recurring": round(share, 3), "sources": row["units"]})
    before = taxonomy_exclusivity(clusters, min_units=2)["score"]
    log: Dict[str, Any] = {
        "node": "value_recoding", "before": before, "after": before,
        "generality_before": generality(clusters), "generality_after": generality(clusters),
        "values_before": sum(len(c.get("values") or []) for c in clusters),
        "selected": selected, "likely_cause_ii": cause_ii, "recoded": [], "kept": [], "rejected": [],
        "failed_calls": [], "operations": [],
    }
    if not selected:
        log["values_after"] = log["values_before"]
        return clusters, log

    by_id = {str(c.get("id")): c for c in clusters}
    structured = model.with_structured_output(RecodingOutput)
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def propose(dim: dict, note: str) -> Optional[RecodingOutput]:
        async with semaphore:
            try:
                messages = VALUE_RECODING_PROMPT.format_messages(use_case=use_case, retry_note=note,
                                                                 **_payload(dim, passages))
                return await structured.ainvoke(messages)
            except Exception as exc:  # noqa: BLE001 — a failed call keeps this dimension unchanged
                logger.warning("Value recoding call failed for dimension %s: %s", dim.get("id"), exc)
                log["failed_calls"].append({"dimension_id": str(dim.get("id")), "error": f"{type(exc).__name__}: {exc}"})
                return None

    async def recode(entry: Mapping[str, Any]) -> None:
        dim = by_id[entry["id"]]
        proposal, note = None, ""
        for attempt in (1, 2):
            proposal = await propose(dim, note)
            if proposal is None:
                return
            problems = validate(dim, proposal, min_sources_per_value)
            if not problems:
                break
            log["rejected"].append({"dimension_id": entry["id"], "attempt": attempt, "problems": problems})
            note = RETRY_NOTE.format(errors="\n".join(f"- {p}" for p in problems))
            proposal = None
        if proposal is None:
            return
        if proposal.keep:
            log["kept"].append({"dimension_id": entry["id"], "rationale": proposal.rationale})
            return
        old_labels = [v.get("label", "") for v in adoptable(dim)]
        fit = apply(dim, proposal)
        log["recoded"].append({"dimension_id": entry["id"], "name": dim.get("name", ""), "rationale": proposal.rationale,
                               "from": old_labels, "to": [v.label for v in proposal.values], **fit})
        log["operations"].append({"dimension_id": entry["id"], "action": "recode",
                                  "message": f"recoded {len(old_labels)} values of dimension {entry['id']} "
                                             f"'{dim.get('name', '')}' as {len(proposal.values)} alternatives"})

    await asyncio.gather(*(recode(e) for e in selected))
    clusters = recompute_evidence(clusters)
    log["after"] = taxonomy_exclusivity(clusters, min_units=2)["score"]
    log["generality_after"] = generality(clusters)
    log["values_after"] = sum(len(c.get("values") or []) for c in clusters)
    fitted = [r for r in log["recoded"] if r.get("fit") is not None]
    log["fit"] = (sum(r["fit"] * r["sources"] for r in fitted) / sum(r["sources"] for r in fitted)) if fitted else None
    return clusters, log


__all__ = ["recode_values", "validate", "apply", "adoptable"]
