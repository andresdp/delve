#!/usr/bin/env python3
r"""Stage funnel (paper plan A10): where along the pipeline each expert option is lost.

Traces every attached ground-truth option of a study through one saved run's
stages (open codes, each saved iteration, the selected view) with the matcher's
embeddings, graded judge and judge cache, and writes, next to the run:

- ``<run>_stage_funnel.csv``: option x stage (present / absent / unjudged), loss stage;
- ``<run>_stage_funnel.json``: counts per view and stage, loss stages, recoveries,
  agreement with the official match file at the selected stage, settings;
- ``<run>_stage_funnel_handcheck.csv``: a seeded sample of options with their
  open-codes verdicts, to hand-check the open-codes candidate gate.

Usage::

    python benchmark/stage_funnel.py examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_20261002_211657.json \\
        --gt benchmark/c2-rl-monitoring/gt --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml \\
        [--match-file examples/c2-rl-monitoring/gt_luna/c2-rl-monitoring_20261002_211657_gt_match.json] \\
        [--out-dir DIR] [--k 5] [--code-fraction 0.02] [--matching-llm openai/...]

The judge is the configured matching LLM (``models.matching_llm``); the funnel's
numbers are diagnostic until the judge is validated against human labels (A6).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from taxonomy_generator.evaluation import stage_funnel  # noqa: E402
from taxonomy_generator.evaluation.gt_match import MatcherError  # noqa: E402
from taxonomy_generator.settings import load_settings  # noqa: E402


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    parser.add_argument("--gt", required=True, help="study ground-truth folder (gt_paper.json / gt_model.json)")
    parser.add_argument("--config", default=None, help="YAML config (models, matcher section)")
    parser.add_argument("--match-file", default=None, help="official *_gt_match.json (default: next to the run)")
    parser.add_argument("--out-dir", default=None, help="output folder (default: next to the run)")
    parser.add_argument("--k", type=int, default=stage_funnel.FunnelSettings.k)
    parser.add_argument("--code-fraction", type=float, default=stage_funnel.FunnelSettings.code_fraction)
    parser.add_argument("--matching-llm", default=None, help="override models.matching_llm")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        from dotenv import load_dotenv
        load_dotenv(HERE.parent / ".env")
    except ImportError:
        pass

    funnel = stage_funnel.FunnelSettings(k=args.k, code_fraction=args.code_fraction)
    try:
        result = asyncio.run(stage_funnel.run_funnel(
            args.taxonomy, args.gt, load_settings(args.config), funnel, matching_llm_override=args.matching_llm,
            match_file=args.match_file, out_dir=args.out_dir))
    except MatcherError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    stages = result["stages"]
    for view, s in result["summary"].items():
        print(f"\n{view} view: {s['options']} options")
        print(f"  {'stage':<14} present  absent  unjudged")
        for stage in stages:
            c = s["per_stage"][stage]
            print(f"  {stage:<14} {c['present']:>7} {c['absent']:>7} {c['unjudged']:>9}")
        print(f"  loss stage: {s['loss_stage']}")
        print(f"  never present: {s['never_present']}; dropped then recovered: {s['dropped_then_recovered']}")
        if "selected_agreement" in s:
            print(f"  selected vs official match: {s['selected_agreement']}")
    for kind, path in result["paths"].items():
        print(f"{kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
