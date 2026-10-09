#!/usr/bin/env python3
"""Compare a decision-focus variant's ground-truth scores with its base run (plan KTD6).

Reads the ``*_gt_metrics.json`` and ``*_gt_match.json`` files that ``python main.py --match-gt``
wrote for a base run and for its variant (``benchmark/focus_variant.py``) and prints:

- the metrics side by side per view (decision P/R/F1 strict and lenient, option P/R/F1,
  exact recall, placement) with the differences;
- **re-judged pairs**: variant pairs labeled by the judge whose ordered texts do not appear
  among the base run's judged pairs (new judge calls, not cache hits);
- **label changes on unchanged pairs** (same system text and same expert option in both runs),
  split by how each label was produced (``label_source`` transition). Only judge-to-judge
  changes indicate judge or cache inconsistency; the others come from the matcher's
  nearest-neighbour routing, which shifts when the set of values changes.

Usage::

    python benchmark/focus_compare.py <base>_gt_metrics.json <variant>_gt_metrics.json [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROWS = [("decision.strict.precision", "Decision P (strict)"), ("decision.strict.recall", "Decision R (strict)"),
        ("decision.strict.f1", "Decision F1 (strict)"), ("decision.lenient.f1", "Decision F1 (lenient)"),
        ("option.precision", "Option P"), ("option.recall", "Option R"), ("option.f1", "Option F1"),
        ("option.exact_recall", "Exact R"), ("placement.accuracy", "Placement")]


def _get(metrics: dict, dotted: str):
    node = metrics
    for key in dotted.split("."):
        node = (node or {}).get(key) if isinstance(node, dict) else None
    return node


def compare_metrics(base: dict, variant: dict) -> dict:
    """Per view and metric: base, variant and difference."""
    out = {}
    for view in ("paper", "model"):
        if view not in base or view not in variant:
            continue
        out[view] = {label: {"base": _get(base[view], key), "variant": _get(variant[view], key),
                             "delta": (round(_get(variant[view], key) - _get(base[view], key), 4)
                                       if isinstance(_get(base[view], key), (int, float))
                                       and isinstance(_get(variant[view], key), (int, float)) else None)}
                     for key, label in ROWS}
    return out


def compare_pairs(base_pairs: list, variant_pairs: list) -> dict:
    """Re-judged pair count and label changes on unchanged pairs, by label-source transition."""
    judged_base = {(p["system_text"], p["gt_text"], p.get("order", "")) for p in base_pairs
                   if p.get("label_source") == "judge"}
    rejudged = sum(1 for p in variant_pairs if p.get("label_source") == "judge"
                   and (p["system_text"], p["gt_text"], p.get("order", "")) not in judged_base)
    base_by_key = {(p["system_text"], p["gt_id"]): p for p in base_pairs}
    unchanged = changed = 0
    transitions: Counter = Counter()
    for p in variant_pairs:
        old = base_by_key.get((p["system_text"], p["gt_id"]))
        if old is None:
            continue
        unchanged += 1
        if old.get("label") != p.get("label"):
            changed += 1
            transitions[f"{old.get('label_source')}->{p.get('label_source')}"] += 1
    return {"variant_pairs": len(variant_pairs), "rejudged": rejudged, "unchanged_pairs": unchanged,
            "label_changes_on_unchanged": changed, "by_transition": dict(transitions)}


def _match_path(metrics_path: Path) -> Path:
    return metrics_path.with_name(metrics_path.name.replace("_gt_metrics.json", "_gt_match.json"))


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base", type=Path, help="base run's *_gt_metrics.json")
    parser.add_argument("variant", type=Path, help="variant's *_gt_metrics.json")
    parser.add_argument("--json", action="store_true", help="print JSON instead of tables")
    args = parser.parse_args(argv)
    base, variant = (json.loads(p.read_text(encoding="utf-8")) for p in (args.base, args.variant))
    result = {"metrics": compare_metrics(base, variant)}
    matches = [_match_path(p) for p in (args.base, args.variant)]
    if all(m.exists() for m in matches):
        result["pairs"] = compare_pairs(*(json.loads(m.read_text(encoding="utf-8"))["pairs"] for m in matches))
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    for view, rows in result["metrics"].items():
        print(f"\n{view} view | base | variant | delta")
        for label, r in rows.items():
            print(f"  {label:<22} | {r['base']} | {r['variant']} | {r['delta']}")
    if "pairs" in result:
        print("\npairs:", json.dumps(result["pairs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
