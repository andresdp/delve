#!/usr/bin/env python3
r"""Design-point sampler (paper plan A12, experiment E13).

Samples design points (one value from each of k dimensions of a run's selected view)
in three groups: attested (one system supports every value, via a passage → system
map such as C3's B7), novel (no system supports them all) and control (a rejected
value, or a value moved in from another dimension). No LLM call. Writes, next to
the run:

- ``<run>_design_points.json``: the points per k and group, with their values,
  evidence passages, systems and the relations among their dimensions, plus
  diagnostics (eligible systems, shortfalls);
- ``<run>_design_points_sheet.csv``: a blind rating sheet. Points are shuffled and
  carry no group; raters give a verdict (workable / conditional / unfeasible), the
  conditions and a reason;
- with ``--describe`` (off by default, to save LLM calls): also
  ``<run>_design_points_descriptions.json``, a short LLM description of each point
  (``describe_design_points.py``; existing descriptions are reused).

Usage::

    python benchmark/design_points.py examples/c3-git-at-scale/c3-git-at-scale_taxonomy_<ts>.json \\
        --systems benchmark/c3-git-at-scale/passage_systems.csv [--attest-by primary] [--k 2 3] [--n 30] [--seed 42] \\
        [--describe [--describe-model openai/gpt-5.6-luna]]

Attested support uses each passage's primary system by default: a passage that mainly
describes one system and mentions another attests only the first.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from taxonomy_generator.evaluation.design_points import load_system_map, sample_points  # noqa: E402


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    parser.add_argument("--systems", help="passage → system map (B7 CSV); omit for no attested group")
    parser.add_argument("--attest-by", choices=["primary", "systems"], default="primary",
                        help="attested support: each passage's primary system only (default, strict) or every "
                             "system it lists")
    parser.add_argument("--k", type=int, nargs="+", default=[2, 3], help="dimensions per point (default: 2 3)")
    parser.add_argument("--n", type=int, default=30, help="points per group and k (default: 30)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=Path, help="default: the run's folder")
    parser.add_argument("--describe", action="store_true",
                        help="also write a short LLM description of each point (off by default: no LLM calls)")
    parser.add_argument("--describe-model", default="openai/gpt-5.6-luna", help="LLM for --describe")
    args = parser.parse_args(argv)

    path = Path(args.taxonomy)
    run = json.loads(path.read_text(encoding="utf-8"))
    clusters = run.get("selected_clusters") or []
    doc_systems = load_system_map(Path(args.systems), args.attest_by) if args.systems else None

    samples = sample_points(clusters, doc_systems, args.k, args.n, args.seed)
    points = [p for s in samples for g in ("attested", "novel", "control") for p in s["groups"][g]]

    out_dir = args.out_dir or path.parent
    stem = path.with_suffix("").name
    out = {"run": str(path), "systems": args.systems, "attest_by": args.attest_by if args.systems else None, "seed": args.seed, "n": args.n, "samples": samples}
    (out_dir / f"{stem}_design_points.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(out_dir / f"{stem}_design_points_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["point_id", "k", "design", "verdict", "conditions", "reason", "rater"])
        for p in sorted(points, key=lambda p: p["point_id"]):
            design = "\n".join(f"{v['dimension']}: {v['label']} — {v['description']}" for v in p["values"])
            w.writerow([p["point_id"], len(p["values"]), design, "", "", "", ""])

    for s in samples:
        d = s["diagnostics"]
        eligible = [name for name, info in d["systems"].items() if info["eligible"]]
        print(f"k={s['k']}: " + ", ".join(f"{g} {c}" for g, c in d["achieved"].items())
              + f" (requested {args.n} each); systems able to attest: {', '.join(eligible) or 'none'}"
              + (f"; {d['note']}" if d["note"] else ""))
    print(f"-> {out_dir / (stem + '_design_points.json')} and _design_points_sheet.csv")
    if args.describe:
        import asyncio
        from dotenv import load_dotenv
        sys.path.insert(0, str(HERE))
        from describe_design_points import run as describe
        load_dotenv()
        asyncio.run(describe(out_dir / f"{stem}_design_points.json", args.describe_model, force=False, concurrency=6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
