#!/usr/bin/env python3
"""Size-matched comparison: Delve's design space cut to the size of the long-context baseline, then re-matched.

Delve outputs 3-4 times as many values as one long-context call (L1), so its option precision, and with it F1, is
lower. This asks whether Delve's best-supported part is as precise as L1. Two cuts of each Delve run's
``selected_clusters``, both sized from the case's L1 runs (means over seeds):

- ``dims``: the first K dimensions in Delve's own selection order (``rank_by_evidence``: supporting sources, then
  exclusivity), with all their values; K = the L1 dimension count.
- ``values``: the N candidate values (outcomes are not scored) with the most supporting sources, then evidence
  codes; N = the L1 candidate count. Dimensions left without values are dropped.

Each cut is written as a run file and scored with ``run_match`` (the run's own config, so the same matcher and
cache: pairs already judged cost nothing). Outputs go under ``output/evaluation/report/size_matched/``.

Usage::

    python benchmark/size_matched.py                  # C1 and C2, both cuts
    python benchmark/size_matched.py --case c2-rl-monitoring --cut values
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import glob
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "output" / "evaluation"
REPORT = OUT / "report" / "size_matched"
CASES = ("c1-ml-workflow", "c2-rl-monitoring")
CUTS = ("dims", "values")
SOURCE_RE = re.compile(r"^(s\d+)_")


def _taxonomies(case: str, folder: str) -> List[Path]:
    return [Path(p) for p in sorted(glob.glob(str(OUT / case / folder / "*_taxonomy_2*.json")))
            if not p.endswith(("_design_points.json", "_descriptions.json"))]


def candidates(clusters: List[Dict]) -> List[Dict]:
    return [v for c in clusters for v in c.get("values") or [] if v.get("status") != "outcome"]


def l1_size(case: str) -> Dict[str, int]:
    """Mean L1 dimension and candidate counts over its seeds, rounded."""
    runs = [json.loads(p.read_text(encoding="utf-8"))["selected_clusters"] for p in _taxonomies(case, "l1_s*")]
    if not runs:
        raise SystemExit(f"no L1 runs for {case}")
    return {"dims": round(statistics.fmean(len(r) for r in runs)),
            "values": round(statistics.fmean(len(candidates(r)) for r in runs))}


def value_sources(value: Dict) -> int:
    return len({m.group(1) for d in value.get("supporting_doc_ids") or [] if (m := SOURCE_RE.match(str(d)))})


def cut_dims(clusters: List[Dict], k: int) -> List[Dict]:
    from taxonomy_generator.nodes.dimension_selector import rank_by_evidence

    return rank_by_evidence(copy.deepcopy(clusters))[:k]


def cut_values(clusters: List[Dict], n: int) -> List[Dict]:
    """Keep the ``n`` candidate values with the most sources (then evidence codes), in their dimensions."""
    ranked = sorted(((ci, vi, v) for ci, c in enumerate(clusters) for vi, v in enumerate(c.get("values") or [])
                     if v.get("status") != "outcome"),
                    key=lambda t: (-value_sources(t[2]), -int(t[2].get("evidence_code_count") or 0), t[0], t[1]))
    keep = {(ci, vi) for ci, vi, _ in ranked[:n]}
    out = []
    for ci, c in enumerate(clusters):
        values = [v for vi, v in enumerate(c.get("values") or []) if (ci, vi) in keep]
        if values:
            out.append({**copy.deepcopy(c), "values": copy.deepcopy(values)})
    return out


async def score(case: str, cut: str, size: Dict[str, int]) -> List[Dict[str, Any]]:
    from taxonomy_generator.evaluation.gt_match import run_match
    from taxonomy_generator.settings import load_settings

    rows = []
    for path in _taxonomies(case, "full_s*"):
        data = json.loads(path.read_text(encoding="utf-8"))
        selected = data["selected_clusters"]
        clusters = cut_dims(selected, size["dims"]) if cut == "dims" else cut_values(selected, size["values"])
        seed = path.parent.name.split("_s")[-1]
        folder = REPORT / case / f"{cut}_s{seed}"
        folder.mkdir(parents=True, exist_ok=True)
        cut_path = folder / path.name.replace("_taxonomy_", f"-{cut}cut_taxonomy_")
        cut_path.write_text(json.dumps({"taxonomy_name": data.get("taxonomy_name"), "mode": f"size-matched-{cut}",
                                        "size_matched": {"cut": cut, "target": size, "from": str(path.relative_to(ROOT))},
                                        "iterations": [{"clusters": clusters}], "selected_clusters": clusters},
                                       ensure_ascii=False), encoding="utf-8")
        settings = load_settings(str(path.parent / "config.yaml"))
        result = await run_match(str(cut_path), str(ROOT / "benchmark" / case / "gt"), settings,
                                 out_dir=str(folder), view="selected")
        for gt_view, m in result["metrics"].items():
            rows.append({"case": case, "cut": cut, "seed": int(seed), "gt_view": gt_view,
                         "dims": len(clusters), "values": len(candidates(clusters)),
                         "option_p": m["option"]["precision"], "option_r": m["option"]["recall"],
                         "option_f1": m["option"]["f1"], "decision_f1_strict": m["decision"]["strict"]["f1"],
                         "decision_f1_lenient": m["decision"]["lenient"]["f1"]})
        print(f"  {case} {cut} seed {seed}: {len(clusters)} dims, {len(candidates(clusters))} values; label sources "
              f"{result['label_sources']}", flush=True)
    return rows


def table(rows: List[Dict[str, Any]]) -> str:
    keys = ("dims", "values", "option_p", "option_r", "option_f1", "decision_f1_strict", "decision_f1_lenient")
    groups: Dict[tuple, List[Dict]] = {}
    for r in rows:
        groups.setdefault((r["case"], r["gt_view"], r["cut"]), []).append(r)
    lines = ["| Case | GT view | Cut | Seeds | Dims | Values | Option P | Option R | Option F1 | Decision F1 strict "
             "| Decision F1 lenient |", "|" + "---|" * 11]
    for (case, view, cut), rs in sorted(groups.items()):
        cells = []
        for k in keys:
            nums = [r[k] for r in rs]
            mean = statistics.fmean(nums)
            cells.append(f"{mean:.2f} [{min(nums):.2f}–{max(nums):.2f}]" if k not in ("dims", "values")
                         else f"{mean:.0f}")
        lines.append(f"| {case} | {view} | {cut} | {' '.join(str(r['seed']) for r in rs)} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--case", choices=CASES, action="append")
    ap.add_argument("--cut", choices=CUTS, action="append")
    args = ap.parse_args(argv)
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    async def run_all() -> List[Dict[str, Any]]:
        rows = []
        for case in args.case or CASES:
            size = l1_size(case)
            print(f"{case}: L1 size {size}", flush=True)
            for cut in args.cut or CUTS:
                rows += await score(case, cut, size)
        return rows

    rows = asyncio.run(run_all())
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "size_matched.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    md = REPORT / "size_matched.md"
    md.write_text("# Size-matched comparison\n\nDelve cut to the long-context baseline's size (selected view); "
                  "mean [min–max] over seeds.\n\n" + table(rows) + "\n", encoding="utf-8")
    print(f"-> {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
