#!/usr/bin/env python3
"""Derive the ``taxonomy.relevance_selection: false`` view of a saved run, without any LLM call.

The use-case relevance filter is the last step of dimension selection; with it off,
selection keeps every dimension of the consolidated taxonomy that passes the support
and decision-point rules (``min_dimension_sources``, ``min_candidate_decisions``).
Both rules are deterministic, so the "filter off" view of a run made with the filter
on can be rebuilt exactly from its saved consolidated taxonomy, instead of paying for
a second pipeline run.

Writes ``<name>-norelevance_taxonomy_<timestamp>.json`` next to the run: a copy of the
run whose ``selected_clusters`` and ``dropped_dimensions`` are the derived ones (and
``relevance_selection: false`` recorded), ready for ``python main.py --match-gt``.

Usage::

    python benchmark/selection_variant.py <run>_taxonomy_<timestamp>.json --config <study config.yaml>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from taxonomy_generator.nodes.dimension_selector import (  # noqa: E402
    split_by_candidates,
    split_by_support,
)
from taxonomy_generator.settings import load_settings  # noqa: E402


def derive(run: dict, min_sources: int, min_candidates: int) -> dict:
    """Return a copy of ``run`` with the structural-rules-only selection of its consolidated taxonomy."""
    final = run["iterations"][-1]["clusters"]
    kept, dropped = split_by_support(final, min_sources)
    kept, dropped_candidates = split_by_candidates(kept, min_candidates)
    out = dict(run)
    out["selected_clusters"] = kept
    out["dropped_dimensions"] = dropped + dropped_candidates
    out["relevance_selection"] = False
    out["derived_from"] = {"selection": "support and decision-point rules only (no LLM relevance filter)",
                           "min_dimension_sources": min_sources, "min_candidate_decisions": min_candidates}
    return out


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    parser.add_argument("--config", required=True, help="the run's YAML config (selection rule settings)")
    args = parser.parse_args(argv)

    path = Path(args.taxonomy)
    if "_taxonomy_" not in path.name:
        print(f"error: not a saved taxonomy file: {path}", file=sys.stderr)
        return 2
    taxonomy = load_settings(args.config).taxonomy
    run = json.loads(path.read_text(encoding="utf-8"))
    out = derive(run, int(taxonomy.min_dimension_sources or 0), int(taxonomy.min_candidate_decisions or 0))
    name, stamp = path.name.split("_taxonomy_", 1)
    target = path.with_name(f"{name}-norelevance_taxonomy_{stamp}")
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"selected {len(out['selected_clusters'])} of {len(run['iterations'][-1]['clusters'])} dimensions "
          f"(relevance filter selected {len(run.get('selected_clusters') or [])}); wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
