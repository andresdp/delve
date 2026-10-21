#!/usr/bin/env python3
"""Replay dimension selection of saved runs with the use-case relevance filter on, then re-match.

The study runs use ``taxonomy.relevance_selection: false``: selection keeps every dimension that passes the support
and decision-point rules. This replays the selection node (``select_dimensions``) on each run's final taxonomy with
the filter on (one generation-model call per run), keeping everything else of the run's config, and scores the
result with ``run_match`` like the run itself.

Check first: the replay with the filter off must reproduce the run's saved selection (same dimension ids);
a run where it does not is reported and skipped.

Outputs: ``output/evaluation/report/relevance_replay/<case>/s<seed>/`` (the replayed run file and its match) and
``relevance_replay.md`` next to them.

Usage::

    python benchmark/relevance_replay.py                       # C2 (default)
    python benchmark/relevance_replay.py --case c1-ml-workflow
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "output" / "evaluation"
REPORT = OUT / "report" / "relevance_replay"


async def select(final: List[Dict], relevance: bool) -> Dict[str, Any]:
    from taxonomy_generator.nodes.dimension_selector import select_dimensions
    from taxonomy_generator.state import State

    return await select_dimensions(State(clusters=[final]), {"configurable": {"relevance_selection": relevance}})


async def replay(case: str) -> List[Dict[str, Any]]:
    from taxonomy_generator.configuration import init_settings
    from taxonomy_generator.evaluation.gt_match import run_match

    rows = []
    for path in sorted(Path(p) for p in glob.glob(str(OUT / case / "full_s*" / "*_taxonomy_2*.json"))
                       if not p.endswith(("_design_points.json", "_descriptions.json"))):
        seed = path.parent.name.split("_s")[-1]
        settings = init_settings(str(path.parent / "config.yaml"))   # the run's config drives the node
        data = json.loads(path.read_text(encoding="utf-8"))
        final = data["iterations"][-1]["clusters"]
        saved = [str(c["id"]) for c in data["selected_clusters"]]
        off = await select(final, relevance=False)
        if [str(c["id"]) for c in off["selected_clusters"][0]] != saved:
            print(f"  seed {seed}: the filter-off replay does not reproduce the saved selection; skipped", flush=True)
            continue
        on = await select(final, relevance=True)
        selected = on["selected_clusters"][0]
        folder = REPORT / case / f"s{seed}"
        folder.mkdir(parents=True, exist_ok=True)
        replayed = folder / path.name.replace("_taxonomy_", "-relevance_taxonomy_")
        replayed.write_text(json.dumps({
            "taxonomy_name": data.get("taxonomy_name"), "mode": "relevance-replay",
            "relevance_replay": {"from": str(path.relative_to(ROOT)), "model": settings.models.generation_llm,
                                 "rationale": (on.get("explanations") or [""])[0]},
            "iterations": [{"clusters": selected}], "selected_clusters": selected,
            "dropped_dimensions": on.get("dropped_dimensions", [])}, ensure_ascii=False, indent=1), encoding="utf-8")
        result = await run_match(str(replayed), str(ROOT / "benchmark" / case / "gt"), settings,
                                 out_dir=str(folder), view="selected")
        values = sum(1 for c in selected for v in c.get("values") or [] if v.get("status") != "outcome")
        for gt_view, m in result["metrics"].items():
            rows.append({"case": case, "seed": int(seed), "gt_view": gt_view, "dims_before": len(saved),
                         "dims": len(selected), "values": values,
                         "option_p": m["option"]["precision"], "option_r": m["option"]["recall"],
                         "option_f1": m["option"]["f1"], "decision_f1_strict": m["decision"]["strict"]["f1"],
                         "decision_f1_lenient": m["decision"]["lenient"]["f1"]})
        kept = {str(c["id"]) for c in selected}
        print(f"  seed {seed}: kept {len(selected)} of {len(saved)} dimensions; dropped: "
              + "; ".join(c.get("name", "") for c in data["selected_clusters"] if str(c["id"]) not in kept), flush=True)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--case", default="c2-rl-monitoring", choices=["c1-ml-workflow", "c2-rl-monitoring"])
    args = ap.parse_args(argv)
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    rows = asyncio.run(replay(args.case))
    if not rows:
        print("nothing replayed", file=sys.stderr)
        return 1
    keys = ("dims", "values", "option_p", "option_r", "option_f1", "decision_f1_strict", "decision_f1_lenient")
    lines = ["| GT view | Seeds | " + " | ".join(keys) + " |", "|" + "---|" * (len(keys) + 2)]
    for view in ("paper", "model"):
        rs = [r for r in rows if r["gt_view"] == view]
        cells = [f"{statistics.fmean(r[k] for r in rs):.2f} [{min(r[k] for r in rs):.2f}–{max(r[k] for r in rs):.2f}]"
                 for k in keys]
        lines.append(f"| {view} | {' '.join(str(r['seed']) for r in rs)} | " + " | ".join(cells) + " |")
    out = REPORT / args.case
    (out / "relevance_replay.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    md = out / "relevance_replay.md"
    md.write_text(f"# Relevance-filter replay: {args.case}\n\nSelected view, filter on; mean [min–max] over seeds."
                  "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"-> {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
