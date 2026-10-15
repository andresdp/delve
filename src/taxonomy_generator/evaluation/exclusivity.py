"""Value exclusivity: does each system take one value per dimension?

A dimension is one design decision and its values are the alternative answers, so a system
should adopt one value per dimension. This module measures that from the evidence, without
an LLM (plan ``docs/plans/2026-10-15-feat-value-exclusivity-plan.md``):

- a **unit** (a system; by default the source of a passage, ``s03`` for ``s03_p02``) adopts
  a candidate value when one of its passages accepts it (``stances.accepted``; for a value
  without stances, its ``supporting_doc_ids`` when its status is ``accepted``). Rejections
  never count;
- a dimension's **exclusivity** is the share of the units adopting any of its candidate values
  that adopt exactly one. A declared hybrid (``hybrids: [{"value_ids": [...]}]`` on the
  dimension) counts as one choice when a unit adopts exactly that set;
- the taxonomy's exclusivity is the mean over dimensions weighted by adopting units.
  Dimensions no unit adopts are left out.

The scoreboard turns it into the **Value exclusivity** row (a penalty fed back to the next
update), and the exclusivity repair step works on the dimensions it ranks lowest.
"""

from __future__ import annotations

import re
from collections import defaultdict
from itertools import combinations
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from taxonomy_generator.nodes.evidence_linker import CANDIDATE_STATUSES, source_of

CRITERION_NAME = "Value exclusivity"
CRITERION_DESCRIPTION = (
    "Each system (source) adopts one value per dimension: the values of a dimension are alternatives, "
    "not features used together. Deterministic: computed from the evidence, without a judge."
)
Unit = Callable[[str], Optional[str]]


def adopting_docs(value: Mapping[str, Any]) -> List[str]:
    """Documents that adopt a candidate value (accepted stance); empty for outcomes."""
    if value.get("status", "accepted") not in CANDIDATE_STATUSES:
        return []
    stances = value.get("stances")
    if isinstance(stances, Mapping) and stances:
        return [str(d) for d in stances.get("accepted") or []]
    if value.get("status", "accepted") == "accepted":
        return [str(d) for d in value.get("supporting_doc_ids") or []]
    return []


def _hybrid_sets(dim: Mapping[str, Any]) -> List[frozenset]:
    out = []
    for h in dim.get("hybrids") or []:
        ids = h.get("value_ids") if isinstance(h, Mapping) else h
        if isinstance(ids, (list, tuple)) and len(ids) >= 2:
            out.append(frozenset(str(i) for i in ids))
    return out


def dimension_exclusivity(dim: Mapping[str, Any], unit: Unit = source_of) -> Dict[str, Any]:
    """Exclusivity of one dimension: adopting units, exclusive units, score and co-adopted pairs.

    ``pairs`` lists every pair of values adopted together by some unit, most units first:
    ``{"values": [id_a, id_b], "labels": [...], "units": [...], "docs": [...]}``. Pairs inside a
    declared hybrid that a unit adopts exactly are not conflicts and are left out.
    """
    labels = {str(v.get("id")): v.get("label", "") for v in dim.get("values") or [] if isinstance(v, Mapping)}
    adopted: Dict[str, Set[str]] = defaultdict(set)          # unit -> value ids
    docs: Dict[Tuple[str, str], Set[str]] = defaultdict(set)  # (unit, value id) -> documents
    for v in dim.get("values") or []:
        if not isinstance(v, Mapping):
            continue
        for doc in adopting_docs(v):
            u = unit(doc)
            if u:
                adopted[u].add(str(v.get("id")))
                docs[(u, str(v.get("id")))].add(doc)
    hybrids = _hybrid_sets(dim)
    exclusive, conflicts = [], {}
    for u, vids in adopted.items():
        if len(vids) == 1 or frozenset(vids) in hybrids:
            exclusive.append(u)
        else:
            conflicts[u] = vids
    pair_units: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for u, vids in conflicts.items():
        for a, b in combinations(sorted(vids, key=_natural), 2):
            pair_units[(a, b)].append(u)
    pairs = [{"values": [a, b], "labels": [labels.get(a, a), labels.get(b, b)], "units": sorted(us, key=_natural),
              "docs": sorted({d for u in us for d in docs[(u, a)] | docs[(u, b)]}, key=_natural)}
             for (a, b), us in pair_units.items()]
    pairs.sort(key=lambda p: (-len(p["units"]), [_natural(i) for i in p["values"]]))
    units = len(adopted)
    return {
        "id": str(dim.get("id")),
        "name": dim.get("name", ""),
        "units": units,
        "exclusive_units": len(exclusive),
        "score": (len(exclusive) / units) if units else None,
        "max_values_per_unit": max((len(v) for v in adopted.values()), default=0),
        "conflicts": {u: sorted(v, key=_natural) for u, v in sorted(conflicts.items(), key=lambda x: _natural(x[0]))},
        "pairs": pairs,
        "hybrids": [sorted(h, key=_natural) for h in hybrids],
    }


def taxonomy_exclusivity(dims: Iterable[Mapping[str, Any]], unit: Unit = source_of) -> Dict[str, Any]:
    """Exclusivity of a taxonomy view: the weighted score and one row per dimension (lowest first)."""
    rows = [dimension_exclusivity(d, unit) for d in dims if isinstance(d, Mapping)]
    scored = [r for r in rows if r["units"]]
    total = sum(r["units"] for r in scored)
    score = sum(r["exclusive_units"] for r in scored) / total if total else None
    scored.sort(key=lambda r: (r["score"], -r["units"], _natural(r["id"])))
    return {"score": score, "units": total, "exclusive_units": sum(r["exclusive_units"] for r in scored),
            "dimensions": scored + [r for r in rows if not r["units"]]}


def feedback(report: Mapping[str, Any], limit: int = 5) -> str:
    """Actionable feedback for the next update: the dimensions whose systems adopt several values."""
    weak = [r for r in report.get("dimensions") or [] if r.get("score") is not None and r["score"] < 1][:limit]
    if not weak:
        return "Every system adopts one value per dimension (or a declared hybrid)."
    lines = []
    for r in weak:
        pair = r["pairs"][0] if r["pairs"] else None
        top = (f"; e.g. values {pair['values'][0]} '{pair['labels'][0]}' and {pair['values'][1]} "
               f"'{pair['labels'][1]}' are adopted together by {', '.join(pair['units'][:4])}") if pair else ""
        lines.append(
            f"- Dimension {r['id']} '{r['name']}': {r['units'] - r['exclusive_units']} of {r['units']} sources adopt "
            f"several of its values (up to {r['max_values_per_unit']}){top}. Values used together are not "
            "alternatives: split the dimension into the questions they answer, move a value that answers a "
            "sub-question to its own dimension, or merge two values that are one option.")
    return "\n".join(lines)


def scoreboard_row(dims: Sequence[Mapping[str, Any]], threshold: float, unit: Unit = source_of) -> Optional[Dict]:
    """The deterministic **Value exclusivity** scoreboard row, or ``None`` when no source adopts any value."""
    report = taxonomy_exclusivity(dims, unit)
    if report["score"] is None:
        return None
    return {"name": CRITERION_NAME, "description": CRITERION_DESCRIPTION, "threshold": threshold,
            "score": float(report["score"]), "passed": bool(report["score"] >= threshold),
            "reason": feedback(report), "evaluated": True, "deterministic": True}


def unit_from_system_map(systems: Mapping[str, Mapping[str, Any]]) -> Unit:
    """A unit function from a passage → system map (``{"passage": {"primary": code}}``); ``GENERAL`` is no system."""
    def unit(doc: str) -> Optional[str]:
        p = (systems.get(str(doc)) or {}).get("primary")
        return p if p and p != "GENERAL" else None
    return unit


def _natural(text: str) -> Tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(text)))


__all__ = ["CRITERION_NAME", "adopting_docs", "dimension_exclusivity", "taxonomy_exclusivity", "feedback",
           "scoreboard_row", "unit_from_system_map"]
