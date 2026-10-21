#!/usr/bin/env python3
"""Graded option score: the strict option precision/recall/F1, with ``related`` counted as half a hit.

The strict score (``gt_match.compute_metrics``) counts a value or an expert option as matched when its best label
is ``same``, ``broader`` or ``narrower``; ``related`` counts as nothing. Most unmatched values overlap an expert option
in part (docs: evaluation record §3.5), so this reports a graded score next to the strict one. The rule was fixed
before computing it (2026-10-17):

- a value scores 1 if it has a hit with an option of the view, else ``--related-weight`` (default 0.5) if it has a
  ``related`` label with one, else 0; an expert option scores the same way from its best label;
- precision = mean value score over the strict precision pool (values whose only hits are options of the other view
  are left out, as in the strict score); recall = mean option score over the view's options; F1 from both.

From the saved ``*_gt_match.json`` files only (no LLM calls). ``--related-weight 0`` must reproduce the strict
scores; the script checks this on every run and stops if it does not.

Usage::

    python benchmark/graded_score.py
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "output" / "evaluation"
REPORT = OUT / "report" / "graded_score"
CASES = ("c1-ml-workflow", "c2-rl-monitoring")
METHODS = {"full": "Delve", "l1": "L1", "l5": "L5"}


def graded(pairs: List[Dict], value_ids: List[str], options, view: str, weight: float) -> Dict[str, float]:
    from taxonomy_generator.evaluation.gt_match import HIT_LABELS

    view_opts = {o.id for o in options if view in o.views}
    other_opts = {o.id for o in options} - view_opts
    hit = {(p["system_id"], p["gt_id"]) for p in pairs if p["label"] in HIT_LABELS}
    rel = {(p["system_id"], p["gt_id"]) for p in pairs if p["label"] == "related"}
    hit_values = {s for s, o in hit if o in view_opts}
    only_other = {s for s, o in hit if o in other_opts} - hit_values
    pool = [v for v in value_ids if v not in only_other]
    rel_values = {s for s, o in rel if o in view_opts}
    v_score = [1.0 if v in hit_values else weight if v in rel_values else 0.0 for v in pool]
    hit_opts = {o for _, o in hit if o in view_opts}
    rel_opts = {o for _, o in rel if o in view_opts}
    o_score = [1.0 if o in hit_opts else weight if o in rel_opts else 0.0 for o in view_opts]
    p = sum(v_score) / len(v_score) if v_score else 0.0
    r = sum(o_score) / len(o_score) if o_score else 0.0
    return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--related-weight", type=float, default=0.5)
    args = ap.parse_args(argv)
    from taxonomy_generator.evaluation.gt_match import ground_truth_options, load_gt_folder, system_values
    from taxonomy_generator.settings import load_settings
    from taxonomy_generator.utils import load_seed_taxonomy

    entries: Dict[str, Dict[str, str]] = {}
    with (OUT / "runs.csv").open(encoding="utf-8") as fh:
        for e in csv.DictReader(fh):
            if e["status"] == "ok" and e["case"] in CASES and e["variant"] in METHODS and e.get("match_selected"):
                entries[e["row"]] = e
    rows = []
    for e in entries.values():
        case = e["case"]
        views = load_gt_folder(ROOT / "benchmark" / case / "gt")
        options = ground_truth_options(views)
        metrics_path = ROOT / e["match_selected"]
        match = json.loads(Path(glob.glob(str(metrics_path.parent / "*_gt_match.json"))[0]).read_text(encoding="utf-8"))
        strict = json.loads(metrics_path.read_text(encoding="utf-8"))
        cfg = ROOT / "examples" / case / f"{case.replace('-', '_')}_config.yaml"
        m = load_settings(str(cfg)).matcher
        values = system_values(load_seed_taxonomy(str(ROOT / e["taxonomy"]), view="selected"),
                               include_outcomes=m.include_outcomes, use_facets=getattr(m, "use_facets", False))
        value_ids = [v.id for v in values]
        for view in views:
            check = graded(match["pairs"], value_ids, options, view, 0.0)
            so = strict[view]["option"]
            if any(abs(check[k] - so[k]) > 1e-3 for k in ("precision", "recall", "f1")):
                print(f"error: {e['row']} {view}: weight 0 gives {check}, strict is "
                      f"{ {k: so[k] for k in ('precision', 'recall', 'f1')} }", file=sys.stderr)
                return 1
            g = graded(match["pairs"], value_ids, options, view, args.related_weight)
            rows.append({"row": e["row"], "case": case, "method": METHODS[e["variant"]], "seed": int(e["seed"]),
                         "gt_view": view, **{f"strict_{k}": so[k] for k in ("precision", "recall", "f1")},
                         **{f"graded_{k}": round(v, 4) for k, v in g.items()}})
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "graded_score.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    cols = ["strict_precision", "strict_recall", "strict_f1", "graded_precision", "graded_recall", "graded_f1"]
    lines = [f"# Graded option score (related = {args.related_weight} of a hit)", "",
             "Selected view; mean [min–max] over seeds. Weight 0 reproduced every strict score (checked).", "",
             "| Case | GT view | Method | Seeds | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 4)]
    groups: Dict[tuple, List[Dict]] = {}
    for r in rows:
        groups.setdefault((r["case"], r["gt_view"], r["method"]), []).append(r)
    order = {"Delve": 0, "L1": 1, "L5": 2}
    for (case, view, method), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], order[kv[0][2]])):
        cells = []
        for c in cols:
            nums = [r[c] for r in rs]
            cells.append(f"{statistics.fmean(nums):.2f} [{min(nums):.2f}–{max(nums):.2f}]")
        lines.append(f"| {case} | {view} | {method} | {' '.join(str(r['seed']) for r in sorted(rs, key=lambda r: r['seed']))} | "
                     + " | ".join(cells) + " |")
    md = REPORT / "graded_score.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"-> {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
