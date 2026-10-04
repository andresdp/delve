#!/usr/bin/env python3
"""Derive the matcher's distance thresholds from the ground truth alone (no system output).

Embeds every attached option of the C1 and C2 ground truth with the matcher's
serialization (``decision › option: description``) and reports cosine
distances between:

- distinct options of the same study: different expert options, which a
  "same" label must never join, so the lower threshold sits below their low tail;
- options of different studies (ML workflow vs. RL monitoring): unrelated
  options, so the upper threshold sits at their low tail, above which pairs are
  labeled "different" without the judge.

Usage: ``python benchmark/frame_thresholds.py [--config config.yaml]``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from taxonomy_generator.evaluation import gt_match  # noqa: E402
from taxonomy_generator.settings import load_settings  # noqa: E402

STUDIES = ("c1-ml-workflow", "c2-rl-monitoring")
PERCENTILES = (0.5, 1, 2, 5, 10, 25, 50)


def load_views(study: str) -> dict:
    folder = HERE / study / "gt"
    return {name: json.loads((folder / f"gt_{name}.json").read_text(encoding="utf-8"))
            for name in ("paper", "model") if (folder / f"gt_{name}.json").exists()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--config", default=None, help="YAML config (embedding model)")
    args = parser.parse_args(argv)
    try:
        from dotenv import load_dotenv
        load_dotenv(HERE.parent / ".env")
    except ImportError:
        pass

    config = gt_match.MatcherConfig.from_settings(load_settings(args.config))
    embed = gt_match.embedder_from_config(config)
    options = {s: gt_match.ground_truth_options(load_views(s)) for s in STUDIES}
    vectors = {s: embed([o.text for o in opts]) for s, opts in options.items()}

    within = []
    for s in STUDIES:
        d = gt_match.pair_distances(vectors[s], vectors[s])
        within.append(d[np.triu_indices(len(d), k=1)])
    within = np.concatenate(within)
    across = gt_match.pair_distances(vectors[STUDIES[0]], vectors[STUDIES[1]]).ravel()

    print(f"embedding: {config.embedding}; options: "
          + ", ".join(f"{s} {len(o)}" for s, o in options.items()))
    for label, values in (("distinct options, same study", within), ("options of different studies", across)):
        pct = ", ".join(f"p{p:g}={np.percentile(values, p):.3f}" for p in PERCENTILES)
        print(f"{label} ({len(values)} pairs): min={values.min():.3f}, {pct}")
    closest = []
    for s in STUDIES:
        d = gt_match.pair_distances(vectors[s], vectors[s])
        iu = np.triu_indices(len(d), k=1)
        for k in np.argsort(d[iu])[:5]:
            i, j = iu[0][k], iu[1][k]
            closest.append((float(d[i, j]), options[s][i].text, options[s][j].text))
    print("closest distinct option pairs:")
    for dist, a, b in sorted(closest)[:8]:
        print(f"  {dist:.3f}  {a[:70]}  <>  {b[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
