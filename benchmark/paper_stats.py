#!/usr/bin/env python3
"""Statistics for the paper (plan §5.3), from the saved matches only (no LLM calls).

Per study (C1, C2) and ground-truth view (paper, model), for Delve (``full``) against each baseline (``l1``, ``l5``):

- **Over seeds:** mean ± sd of strict option P/R/F1 and decision F1 (lenient), and Cliff's δ of option F1 (Delve's
  seeds vs the baseline's). With 3 seeds per side, δ is descriptive only.
- **Paired over expert options** (the units): each option's recovery rate = the share of a system's seeds that
  match it. The recall difference Delve − baseline gets a paired bootstrap CI over options (10,000 resamples,
  seeded); McNemar's exact test compares seed 42 of both (options recovered by one and not the other).
- **Minimum detectable difference:** with n options, a recall difference smaller than about
  ``1.96 * sqrt(2 * p * (1 - p) / n)`` (p = pooled recall) cannot be told apart from noise; reported per study.

Ablations (A1–A4, one seed) are listed against their seed-42 full run with the full system's seed range, since one
seed supports no interval. Outputs: ``output/evaluation/report/paper_stats/`` (Markdown and JSON).

Usage::

    python benchmark/paper_stats.py
"""

from __future__ import annotations

import csv
import glob
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "output" / "evaluation"
REPORT = OUT / "report" / "paper_stats"
CASES = ("c1-ml-workflow", "c2-rl-monitoring")
SYSTEMS = {"full": "Delve", "l1": "L1", "l5": "L5"}
B = 10_000


def cliffs_delta(a: List[float], b: List[float]) -> float:
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    return (gt - lt) / (len(a) * len(b))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value for b and c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def recovered(match_dir: Path, view_opts: set) -> set:
    from taxonomy_generator.evaluation.gt_match import HIT_LABELS

    pairs = json.loads(Path(glob.glob(str(match_dir / "*_gt_match.json"))[0]).read_text(encoding="utf-8"))["pairs"]
    return {p["gt_id"] for p in pairs if p["label"] in HIT_LABELS and p["gt_id"] in view_opts}


def main() -> int:
    from taxonomy_generator.evaluation.gt_match import ground_truth_options, load_gt_folder

    entries: Dict[str, Dict[str, str]] = {}
    with (OUT / "runs.csv").open(encoding="utf-8") as fh:
        for e in csv.DictReader(fh):
            if e["status"] == "ok" and e.get("match_selected"):
                entries[e["row"]] = e
    rng = random.Random(42)
    results, lines = [], ["# Statistics for the paper", "",
                          "Strict option scores, selected view. Over seeds: mean ± sd. Paired: over expert options "
                          f"({B:,} bootstrap resamples). 3 seeds per system: δ and McNemar are descriptive.", ""]
    for case in CASES:
        views = load_gt_folder(ROOT / "benchmark" / case / "gt")
        options = ground_truth_options(views)
        for view in views:
            view_opts = {o.id for o in options if view in o.views}
            per_sys: Dict[str, Dict] = {}
            for variant, name in SYSTEMS.items():
                runs = sorted((e for e in entries.values() if e["case"] == case and e["variant"] == variant),
                              key=lambda e: int(e["seed"]))
                if not runs:
                    continue
                metrics = [json.loads((ROOT / e["match_selected"]).read_text(encoding="utf-8"))[view] for e in runs]
                rec = {int(e["seed"]): recovered((ROOT / e["match_selected"]).parent, view_opts) for e in runs}
                per_sys[name] = {
                    "seeds": [int(e["seed"]) for e in runs],
                    "f1": [m["option"]["f1"] for m in metrics], "p": [m["option"]["precision"] for m in metrics],
                    "r": [m["option"]["recall"] for m in metrics],
                    "dec": [m["decision"]["lenient"]["f1"] for m in metrics],
                    "rate": {o: sum(o in s for s in rec.values()) / len(rec) for o in view_opts}, "rec": rec}
            n = len(view_opts)
            lines += [f"## {case}, {view} view ({n} expert options)", "",
                      "| System | Seeds | Option P | Option R | Option F1 | Decision F1 lenient |", "|---|---|---|---|---|---|"]
            fmt = lambda xs: f"{statistics.fmean(xs):.2f} ± {statistics.stdev(xs):.2f}" if len(xs) > 1 else f"{xs[0]:.2f}"  # noqa: E731
            for name, s in per_sys.items():
                lines.append(f"| {name} | {len(s['seeds'])} | {fmt(s['p'])} | {fmt(s['r'])} | {fmt(s['f1'])} | {fmt(s['dec'])} |")
            delve = per_sys.get("Delve")
            pooled = statistics.fmean(statistics.fmean(s["r"]) for s in per_sys.values())
            mdd = 1.96 * math.sqrt(2 * pooled * (1 - pooled) / n)
            lines += ["", f"Minimum detectable recall difference (n = {n}, pooled recall {pooled:.2f}): about "
                          f"±{mdd:.2f}.", "",
                      "| Delve vs | Δ option F1 (means) | Cliff's δ (F1, seeds) | Δ recall, paired over options [95% CI] | "
                      "McNemar, seed 42 (Delve only / other only, p) |", "|---|---|---|---|---|"]
            opts = sorted(view_opts)
            for name in ("L1", "L5"):
                other = per_sys.get(name)
                if not (delve and other):
                    continue
                diffs = [delve["rate"][o] - other["rate"][o] for o in opts]
                point = statistics.fmean(diffs)
                boots = sorted(statistics.fmean(rng.choices(diffs, k=n)) for _ in range(B))
                lo, hi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
                d42, o42 = delve["rec"].get(42, set()), other["rec"].get(42, set())
                only_d, only_o = len(d42 - o42), len(o42 - d42)
                row = {"case": case, "view": view, "vs": name, "n_options": n, "mdd_recall": round(mdd, 3),
                       "delta_f1": round(statistics.fmean(delve["f1"]) - statistics.fmean(other["f1"]), 3),
                       "cliffs_delta_f1": round(cliffs_delta(delve["f1"], other["f1"]), 3),
                       "delta_recall": round(point, 3), "ci": [round(lo, 3), round(hi, 3)],
                       "mcnemar_seed42": {"delve_only": only_d, "other_only": only_o,
                                          "p": round(mcnemar_exact(only_d, only_o), 4)}}
                results.append(row)
                lines.append(f"| {name} | {row['delta_f1']:+.2f} | {row['cliffs_delta_f1']:+.2f} | {point:+.2f} "
                             f"[{lo:+.2f}, {hi:+.2f}] | {only_d} / {only_o}, p = {row['mcnemar_seed42']['p']:.3f} |")
            lines.append("")

    lines += ["## Ablations (one seed; against the seed-42 full run and the full system's seed range)", "",
              "| Case | Ablation | Option F1 paper / model | Recall paper | Decision F1 lenient paper / model | "
              "Full seed 42 F1 | Full seed range F1 |", "|---|---|---|---|---|---|---|"]
    for case in CASES:
        full = sorted((e for e in entries.values() if e["case"] == case and e["variant"] == "full"), key=lambda e: e["seed"])
        fm = [json.loads((ROOT / e["match_selected"]).read_text(encoding="utf-8")) for e in full]
        f42 = next(m for e, m in zip(full, fm) if e["seed"] == "42")
        rng_txt = " / ".join(f"{min(m[v]['option']['f1'] for m in fm):.2f}–{max(m[v]['option']['f1'] for m in fm):.2f}"
                             for v in ("paper", "model"))
        for e in sorted((e for e in entries.values() if e["case"] == case and e["variant"] in ("nofeedback", "rewrite")),
                        key=lambda e: e["row"]):
            m = json.loads((ROOT / e["match_selected"]).read_text(encoding="utf-8"))
            lines.append(f"| {case} | {e['row']} {e['variant']} | {m['paper']['option']['f1']:.2f} / "
                         f"{m['model']['option']['f1']:.2f} | {m['paper']['option']['recall']:.2f} | "
                         f"{m['paper']['decision']['lenient']['f1']:.2f} / {m['model']['decision']['lenient']['f1']:.2f} | "
                         f"{f42['paper']['option']['f1']:.2f} / {f42['model']['option']['f1']:.2f} | {rng_txt} |")
    lines += ["", "A4 (C2 rewrite) ended with an empty space and has no match; its last non-empty draft is scored "
                  "separately (record §3.11)."]
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "paper_stats.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    md = REPORT / "paper_stats.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
