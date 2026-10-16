#!/usr/bin/env python3
"""Replay a saved run from consolidation onward, with other settings (offline A/B; value recoding plan).

Takes the run's reviewed taxonomy (the iteration before consolidation), its open codes and its documents, and
runs again: dimension merging and value consolidation, evidence linking, the steps after it (exclusivity repair,
value recoding), selection, and the final scoreboard. Mining is not repeated, so comparing two replays of the
same run (e.g. ``value_recoding`` off and on) removes run-to-run variation of the mining. Plans
2026-10-15-feat-value-exclusivity and 2026-10-15-feat-value-recoding report results obtained this way.

Needs the run's ``*_open_codes_<ts>.json`` and ``*_documents_<ts>.json`` next to its taxonomy (they contain
source text and are not committed: rebuild them by running the study). Writes a taxonomy JSON (``iterations``,
``selected_clusters``, ``dropped_dimensions``, ``evaluation``, ``operation_log``) ready for
``python main.py --match-gt``. Biplots are not written.

Usage::

    python benchmark/replay_consolidation.py examples/c1-ml-workflow/c1-ml-workflow_taxonomy_20261002_185546.json \\
        --config examples/c1-ml-workflow/c1_ml_workflow_config.yaml --set value_recoding=true --out replay_on.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from dotenv import load_dotenv  # noqa: E402

RUN = re.compile(r"^(?P<prefix>.+)_taxonomy_(?P<stamp>\d{8}_\d{6})\.json$")


def _value(text: str):
    """A ``--set`` value: JSON when it parses (true, 0.5, null, [..]), else the string."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="the saved run: <prefix>_taxonomy_<timestamp>.json")
    parser.add_argument("--config", required=True, help="the study config the run used")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                        help="override a configuration field, e.g. value_recoding=true (repeatable)")
    parser.add_argument("--out", required=True, help="where to write the replayed taxonomy JSON")
    parser.add_argument("--no-evaluate", action="store_true", help="skip the final scoreboard (no judge calls)")
    return parser.parse_args(argv)


async def replay(args: argparse.Namespace) -> dict:
    from taxonomy_generator.configuration import init_settings

    init_settings(args.config)
    from taxonomy_generator.nodes.dimension_selector import select_dimensions
    from taxonomy_generator.nodes.taxonomy_evaluator import evaluate_taxonomy
    from taxonomy_generator.nodes.value_consolidator import consolidate_values
    from taxonomy_generator.state import State

    path = Path(args.taxonomy)
    match = RUN.match(path.name)
    if not match:
        raise SystemExit(f"not a run taxonomy (<prefix>_taxonomy_<timestamp>.json): {path.name}")
    prefix, stamp = match["prefix"], match["stamp"]
    run = json.loads(path.read_text())
    codes = json.loads((path.parent / f"{prefix}_open_codes_{stamp}.json").read_text())["open_codes"]
    docs = json.loads((path.parent / f"{prefix}_documents_{stamp}.json").read_text())["documents"]
    reviewed = run["iterations"][-2]["clusters"]  # the last iteration is the consolidation

    overrides = {"visualization_enabled": False}
    for item in args.set:
        key, sep, raw = item.partition("=")
        if not sep:
            raise SystemExit(f"--set expects KEY=VALUE, got {item!r}")
        overrides[key.strip()] = _value(raw.strip())
    config = {"configurable": overrides}

    state = State(clusters=[reviewed], open_codes=codes, documents=docs)
    consolidated = await consolidate_values(state, config)
    state = State(clusters=[reviewed] + consolidated["clusters"], open_codes=codes, documents=docs)
    selected = await select_dimensions(state, config)
    state = State(clusters=state.clusters, open_codes=codes, documents=docs,
                  selected_clusters=selected["selected_clusters"],
                  dropped_dimensions=selected.get("dropped_dimensions", []))
    evaluation = None if args.no_evaluate else (await evaluate_taxonomy(state, config))["evaluation"]
    return {
        **{k: run[k] for k in ("taxonomy_name", "mode") if k in run},
        "replayed_from": {"taxonomy": str(path), "config": args.config, "overrides": overrides},
        "iterations": [{"explanation": "", "clusters": c} for c in state.clusters],
        "selected_clusters": selected["selected_clusters"][-1],
        "dropped_dimensions": selected.get("dropped_dimensions", []),
        "evaluation": evaluation,
        "operation_log": consolidated.get("operation_log", []),
    }


def main(argv=None) -> None:
    load_dotenv()
    args = parse_args(argv)
    result = asyncio.run(replay(args))
    Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
