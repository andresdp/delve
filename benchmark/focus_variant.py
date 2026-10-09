#!/usr/bin/env python3
"""Build a decision-focus variant of a saved run (offline A/B; plan 2026-10-08-1500 decision-focus pass).

Takes the run's final consolidated taxonomy (``iterations[-1].clusters``), applies the
decision-focus passes of ``taxonomy_generator.nodes.decision_focus`` in the order the
variant names (``merge``, ``rehome`` or ``merge-rehome``), recomputes evidence summaries,
and re-applies selection's structural rules (``min_dimension_sources``,
``min_candidate_decisions``). The LLM relevance filter is not applied (as in the study
configs). Comparing a variant with its own base run removes run-to-run variation.

Writes ``<name>-<variant>_taxonomy_<timestamp>.json`` next to the run: a copy of the run
whose ``selected_clusters`` and ``dropped_dimensions`` are the derived ones, with
``derived_from`` (variant, model, date) and the ``decision_focus_log`` (applied, rejected
and failed operations), ready for ``python main.py --match-gt``.

Usage::

    python benchmark/focus_variant.py <run>_taxonomy_<ts>.json --config <study config.yaml> --variant merge
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from dotenv import load_dotenv  # noqa: E402

from taxonomy_generator.nodes.decision_focus import apply_passes  # noqa: E402
from taxonomy_generator.nodes.dimension_selector import split_by_candidates, split_by_support  # noqa: E402
from taxonomy_generator.settings import load_settings  # noqa: E402
from taxonomy_generator.utils import load_chat_model  # noqa: E402

VARIANTS = {"merge": ["merge"], "rehome": ["rehome"], "merge-rehome": ["merge", "rehome"]}


async def derive(run: dict, model: Any, use_case: str, passes: Sequence[str], min_sources: int,
                 min_candidates: int, variant: str, model_name: str) -> dict:
    """Return a copy of ``run`` whose selection is the focused, structurally re-selected taxonomy."""
    consolidated = copy.deepcopy(run["iterations"][-1]["clusters"])
    focused, log = await apply_passes(consolidated, model, use_case, passes)
    kept, dropped = split_by_support(focused, min_sources)
    kept, dropped_candidates = split_by_candidates(kept, min_candidates)
    out = dict(run)
    out["selected_clusters"] = kept
    out["dropped_dimensions"] = dropped + dropped_candidates
    out["relevance_selection"] = False
    out["decision_focus_log"] = log
    out["derived_from"] = {"variant": variant, "passes": list(passes), "model": model_name,
                           "date": dt.date.today().isoformat(),
                           "selection": "support and decision-point rules only (no LLM relevance filter)",
                           "min_dimension_sources": min_sources, "min_candidate_decisions": min_candidates}
    return out


def main(argv=None, model: Any = None) -> int:
    """Run the command line; return the exit code. ``model`` overrides the config's LLM (tests)."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    parser.add_argument("--config", required=True, help="the run's YAML config (use case, LLM, selection rules)")
    parser.add_argument("--variant", required=True, choices=sorted(VARIANTS))
    args = parser.parse_args(argv)

    path = Path(args.taxonomy)
    if "_taxonomy_" not in path.name:
        print(f"error: not a saved taxonomy file: {path}", file=sys.stderr)
        return 2
    settings = load_settings(args.config)
    model_name = "injected" if model is not None else settings.models.generation_llm
    if model is None:
        load_dotenv()
        model = load_chat_model(model_name)
    run = json.loads(path.read_text(encoding="utf-8"))
    out = asyncio.run(derive(run, model, settings.taxonomy.use_case, VARIANTS[args.variant],
                             int(settings.taxonomy.min_dimension_sources or 0),
                             int(settings.taxonomy.min_candidate_decisions or 0), args.variant, model_name))
    name, stamp = path.name.split("_taxonomy_", 1)
    target = path.with_name(f"{name}-{args.variant}_taxonomy_{stamp}")
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {entry["pass"]: (len(entry["applied"]), len(entry["rejected"]), len(entry["failed_calls"]))
              for entry in out["decision_focus_log"]}
    print(f"{args.variant}: {len(run['iterations'][-1]['clusters'])} consolidated -> "
          f"{len(out['selected_clusters'])} selected dimensions; applied/rejected/failed per pass {counts}; "
          f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
