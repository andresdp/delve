"""Design-point sampler (paper plan A12, experiment E13).

A *design point* takes one value from each of k distinct dimensions of a run's
selected view: one concrete way to combine the mined decisions. Points are drawn,
with a fixed seed, in three groups:

- ``attested``: every value is supported by passages of one and the same system
  (needs a passage → system map, e.g. C3's B7). Systems are visited in turn, so
  thinly documented systems still get their share when they can supply k dimensions.
- ``novel``: candidate values with no system supporting all of them. Exploring such
  combinations is one purpose of the design space; whether a novel point is
  workable is judged later, not assumed.
- ``control``: points that should fail. ``rejected_value`` puts a value the sources
  rejected in one slot; ``misplaced_value`` fills one slot with a candidate value taken
  from a dimension outside the point.

Candidate values are those with status ``accepted`` or ``mixed``; ``outcome`` values
(effects of decisions) are never sampled. Relations between a point's dimensions are
copied onto the point. They are dimension-level, so no value-level violation is
inferred from them. Without a system map, every point that is not a control lands in
``novel``, and ``attested`` stays empty.
"""

from __future__ import annotations

import csv
import random
from itertools import cycle
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

CANDIDATE = ("accepted", "mixed")


def load_system_map(path: Path, attest_by: str = "systems") -> Dict[str, Set[str]]:
    """Passage/document id → set of systems from a B7-style CSV (``#`` lines skipped, ``GENERAL`` dropped).

    ``attest_by="primary"`` keeps only each passage's primary system: a passage that
    mainly describes one system and mentions another then attests only the first.
    ``"systems"`` uses every listed system (looser).
    """
    if attest_by not in ("primary", "systems"):
        raise ValueError(f"attest_by must be 'primary' or 'systems', got {attest_by!r}")
    with open(path, encoding="utf-8", newline="") as f:
        lines = [line for line in f if not line.lstrip().startswith("#")]
    out: Dict[str, Set[str]] = {}
    for row in csv.DictReader(lines):
        column = row.get(attest_by) or ""
        systems = {s.strip() for s in column.split(";") if s.strip()}
        out[row["passage_id"].strip()] = systems - {"GENERAL"}
    return out


def _systems_of(value: Mapping[str, Any], doc_systems: Optional[Mapping[str, Set[str]]]) -> Set[str]:
    if not doc_systems:
        return set()
    found: Set[str] = set()
    for doc in value.get("supporting_doc_ids") or []:
        found |= doc_systems.get(str(doc), set())
    return found


def _slot(dim: Mapping[str, Any], value: Mapping[str, Any], systems: Set[str],
          origin: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "dimension_id": str(dim.get("id")),
        "dimension": dim.get("name", ""),
        "value_id": str(value.get("id")),
        "label": value.get("label", ""),
        "description": value.get("description", ""),
        "status": value.get("status", ""),
        "supporting_doc_ids": list(value.get("supporting_doc_ids") or []),
        "systems": sorted(systems),
        "origin_dimension_id": str((origin or dim).get("id")),
    }


def _relations(dims: Iterable[Mapping[str, Any]]) -> List[Dict[str, str]]:
    ids = {str(d.get("id")) for d in dims}
    rels = []
    for d in dims:
        for r in d.get("relations") or []:
            target = str(r.get("target_id"))
            if target in ids and target != str(d.get("id")):
                rels.append({"source": str(d.get("id")), "target": target, "type": r.get("type", "")})
    return rels


def sample_design_points(clusters: List[Mapping[str, Any]], doc_systems: Optional[Mapping[str, Set[str]]],
                         k: int, n: int, seed: int) -> Dict[str, Any]:
    """Sample up to ``n`` points per group with ``k`` dimensions each; see the module docstring."""
    rng = random.Random(seed)
    dims = [c for c in clusters if isinstance(c, dict)]
    by_id = {str(d.get("id")): d for d in dims}
    systems_of = {str(v.get("id")): _systems_of(v, doc_systems) for d in dims for v in d.get("values") or []}
    candidates = {str(d.get("id")): [v for v in d.get("values") or [] if v.get("status") in CANDIDATE] for d in dims}
    candidate_dims = sorted(i for i, vals in candidates.items() if vals)
    rejected = [(str(d.get("id")), v) for d in dims for v in d.get("values") or [] if v.get("status") == "rejected"]

    groups: Dict[str, List[Dict[str, Any]]] = {"attested": [], "novel": [], "control": []}
    all_systems = sorted(set().union(*systems_of.values())) if systems_of else []
    per_system: Dict[str, Dict[str, List[Mapping[str, Any]]]] = {
        s: {i: [v for v in candidates[i] if s in systems_of[str(v.get("id"))]] for i in candidate_dims}
        for s in all_systems}
    per_system = {s: {i: vals for i, vals in m.items() if vals} for s, m in per_system.items()}
    diagnostics: Dict[str, Any] = {
        "k": k, "requested_per_group": n, "seed": seed, "system_map": bool(doc_systems),
        "candidate_dimensions": len(candidate_dims), "rejected_values": len(rejected),
        "systems": {s: {"dimensions": len(m), "eligible": len(m) >= k} for s, m in per_system.items()},
        "note": "",
    }
    if len(candidate_dims) < k:
        diagnostics["note"] = f"only {len(candidate_dims)} dimensions with candidate values; k={k} impossible"
        diagnostics["achieved"] = {g: 0 for g in groups}
        return {"groups": groups, "diagnostics": diagnostics}

    seen: Set[Any] = set()
    budget = 200 * max(n, 1)

    def add(group: str, slots: List[Dict[str, Any]], **extra: Any) -> bool:
        key = (group, extra.get("control"), frozenset((s["dimension_id"], s["value_id"]) for s in slots))
        if key in seen:
            return False
        seen.add(key)
        chosen = [by_id[s["dimension_id"]] for s in slots]
        groups[group].append({"group": group, **extra, "values": sorted(slots, key=lambda s: s["dimension_id"]),
                              "relations": _relations(chosen)})
        return True

    # Attested: visit eligible systems in turn.
    eligible = [s for s in all_systems if len(per_system[s]) >= k]
    if eligible:
        turns, misses = cycle(eligible), 0
        while len(groups["attested"]) < n and misses < budget:
            s = next(turns)
            picked = rng.sample(sorted(per_system[s]), k)
            slots = [_slot(by_id[i], v, systems_of[str(v.get("id"))])
                     for i in picked for v in [rng.choice(per_system[s][i])]]
            misses += 0 if add("attested", slots, system=s) else 1

    # Novel: candidate values with no common system.
    misses = 0
    while len(groups["novel"]) < n and misses < budget:
        picked = rng.sample(candidate_dims, k)
        vals = [rng.choice(candidates[i]) for i in picked]
        common = set.intersection(*[systems_of[str(v.get("id"))] for v in vals]) if doc_systems else set()
        if common:
            misses += 1
            continue
        slots = [_slot(by_id[i], v, systems_of[str(v.get("id"))]) for i, v in zip(picked, vals)]
        misses += 0 if add("novel", slots) else 1

    # Controls: half rejected-value, half misplaced-value (all misplaced when nothing was rejected).
    n_rejected = n // 2 if rejected else 0
    misses = 0
    while sum(p["control"] == "rejected_value" for p in groups["control"]) < n_rejected and misses < budget:
        dim_id, bad = rng.choice(rejected)
        others = [i for i in candidate_dims if i != dim_id]
        if len(others) < k - 1:
            break
        picked = rng.sample(others, k - 1)
        slots = [_slot(by_id[dim_id], bad, systems_of[str(bad.get("id"))])]
        slots += [_slot(by_id[i], v, systems_of[str(v.get("id"))]) for i in picked for v in [rng.choice(candidates[i])]]
        misses += 0 if add("control", slots, control="rejected_value") else 1
    misses = 0
    while len(groups["control"]) < n and misses < budget and len(candidate_dims) > k:
        picked = rng.sample(candidate_dims, k)
        target = rng.choice(picked)
        origin_id = rng.choice([i for i in candidate_dims if i not in picked])
        stray = rng.choice(candidates[origin_id])
        slots = []
        for i in picked:
            if i == target:
                slots.append(_slot(by_id[i], stray, systems_of[str(stray.get("id"))], origin=by_id[origin_id]))
            else:
                v = rng.choice(candidates[i])
                slots.append(_slot(by_id[i], v, systems_of[str(v.get("id"))]))
        misses += 0 if add("control", slots, control="misplaced_value") else 1

    diagnostics["achieved"] = {g: len(p) for g, p in groups.items()}
    short = [g for g, c in diagnostics["achieved"].items() if c < n and (g != "attested" or doc_systems)]
    if short:
        diagnostics["note"] = "fewer distinct points than requested for: " + ", ".join(short)
    return {"groups": groups, "diagnostics": diagnostics}
