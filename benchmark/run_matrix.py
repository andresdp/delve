#!/usr/bin/env python3
"""Sequential runner for the evaluation matrix (docs/plans/2026-10-15-feat-evaluation-runs-plan.md, step 5).

Runs the named rows one at a time, in the order given. For each row:

1. a seed-specific copy of the case config is written into the row's output folder (``pipeline.random_seed``,
   ``taxonomy.name`` with the variant and seed, plus the row's overrides);
2. ``python main.py --corpus <corpus> --config <copy> --output <dir>`` (or ``benchmark/baselines.py`` for the
   baseline rows);
3. ``python main.py --match-gt <taxonomy> --gt benchmark/<case>/gt`` for both views (``selected``, ``final``)
   when the case has an expert model (C1, C2);
4. one line is appended to ``output/evaluation/runs.csv``.

A failed step is retried once. If it fails again, the row is recorded as failed and the runner stops: it never
skips ahead. A row whose folder already holds a taxonomy is skipped (``--force`` re-runs it).

Usage::

    python benchmark/run_matrix.py --list
    python benchmark/run_matrix.py S1 S2 S3            # the smoke run
    python benchmark/run_matrix.py M1 M2 M3 --dry-run   # print the commands only
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "evaluation"
LOG = OUT / "runs.csv"
COLUMNS = ["row", "case", "variant", "seed", "status", "attempts", "total_tokens", "elapsed_seconds",
           "taxonomy", "match_selected", "match_final", "started", "finished"]

CASES = {
    "c1-ml-workflow": ("examples/c1-ml-workflow", "c1_ml_workflow"),
    "c2-rl-monitoring": ("examples/c2-rl-monitoring", "c2_rl_monitoring"),
    "c3-git-at-scale": ("examples/c3-git-at-scale", "c3_git_at_scale"),
}
MATCHED = {"c1-ml-workflow", "c2-rl-monitoring"}          # cases with an expert model under benchmark/<case>/gt


@dataclass
class Row:
    id: str
    case: str
    variant: str                     # full | nofeedback | rewrite | sample | sample-nofeedback | l1 | l5
    seed: int
    overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def baseline(self) -> Optional[str]:
        return {"l1": "long_context", "l5": "prior_knowledge"}.get(self.variant)

    @property
    def config(self) -> Path:
        folder, stem = CASES[self.case]
        suffix = {"nofeedback": "_nofeedback", "rewrite": "_rewrite",       # full and baselines: the study config
                  "sample": "_sample", "sample-nofeedback": "_sample"}.get(self.variant, "")
        return ROOT / folder / f"{stem}{suffix}_config.yaml"

    @property
    def corpus(self) -> Path:
        folder, _ = CASES[self.case]
        return ROOT / folder / f"{self.case}_corpus.json"

    @property
    def out(self) -> Path:
        return OUT / self.case / f"{self.variant}_s{self.seed}"


def _matrix() -> Dict[str, Row]:
    rows: List[Row] = [
        # Smoke (step 4): the C3 sample, the same with the critic's feedback off, one L5 call for C2.
        Row("S1", "c3-git-at-scale", "sample", 42),
        Row("S2", "c3-git-at-scale", "sample-nofeedback", 42, {"evaluation": {"loop_feedback": False}}),
        Row("S3", "c2-rl-monitoring", "l5", 42),
    ]
    seeds = (42, 43, 44)
    for i, (case, seed) in enumerate([(c, s) for c in ("c1-ml-workflow", "c2-rl-monitoring", "c3-git-at-scale")
                                      for s in seeds], start=1):
        rows.append(Row(f"M{i}", case, "full", seed))
    for i, (case, kind, seed) in enumerate([(c, k, s) for c in ("c1-ml-workflow", "c2-rl-monitoring")
                                            for k in ("l1", "l5") for s in seeds], start=1):
        rows.append(Row(f"B{i}", case, kind, seed))
    ablations = [(c, v, 42) for v in ("nofeedback", "rewrite") for c in ("c1-ml-workflow", "c2-rl-monitoring")]
    ablations += [(c, v, 43) for v in ("nofeedback", "rewrite") for c in ("c1-ml-workflow", "c2-rl-monitoring")]
    for i, (case, variant, seed) in enumerate(ablations, start=1):
        rows.append(Row(f"A{i}", case, variant, seed))
    return {r.id: r for r in rows}


MATRIX = _matrix()


def rel(path: Path) -> str:
    """The path relative to the repository when it is inside it."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_config(row: Row) -> Path:
    """The row's config: the case config with its seed, a distinct name and the row's overrides."""
    data = yaml.safe_load(row.config.read_text(encoding="utf-8"))
    data.setdefault("pipeline", {})["random_seed"] = row.seed
    data.setdefault("taxonomy", {})["name"] = f"{row.case}-{row.variant}-s{row.seed}"
    for section, values in row.overrides.items():
        data.setdefault(section, {}).update(values)
    row.out.mkdir(parents=True, exist_ok=True)
    path = row.out / "config.yaml"
    header = f"# Generated by benchmark/run_matrix.py for row {row.id} from {rel(row.config)}\n"
    path.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def taxonomy_file(row: Row) -> Optional[Path]:
    found = sorted(p for p in row.out.glob("*_taxonomy_*.json")
                   if not p.name.endswith(("_design_points.json", "_descriptions.json")))
    return found[-1] if found else None


def commands(row: Row, config: Path) -> List[List[str]]:
    py = sys.executable
    if row.baseline:
        return [[py, str(ROOT / "benchmark" / "baselines.py"), "--case", row.case, "--kind", row.baseline,
                 "--seed", str(row.seed), "--out", str(row.out)]]
    return [[py, str(ROOT / "main.py"), "--corpus", str(row.corpus), "--config", str(config),
             "--output", str(row.out)]]


def match_commands(row: Row, taxonomy: Path, config: Path) -> Dict[str, List[str]]:
    if row.case not in MATCHED:
        return {}
    gt = ROOT / "benchmark" / row.case / "gt"
    cfg = row.config if row.baseline else config
    return {view: [sys.executable, str(ROOT / "main.py"), "--match-gt", str(taxonomy), "--gt", str(gt),
                   "--config", str(cfg), "--gt-view", view, "--output", str(row.out / f"match_{view}")]
            for view in ("selected", "final")}


def run_step(cmd: List[str], log_path: Path, dry_run: bool) -> tuple[bool, int]:
    """Run once, retry once on failure. Output is appended to the row's log file."""
    print("  $ " + " ".join(cmd), flush=True)
    if dry_run:
        return True, 0
    for attempt in (1, 2):
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n=== {dt.datetime.now().isoformat(timespec='seconds')} attempt {attempt}: "
                     f"{' '.join(cmd)}\n")
            fh.flush()
            code = subprocess.call(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT)
        if code == 0:
            return True, attempt
        print(f"  ! exit {code} (attempt {attempt}); see {log_path}", flush=True)
    return False, 2


def record(entry: Dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        if new:
            writer.writeheader()
        writer.writerow({k: entry.get(k, "") for k in COLUMNS})


def run_row(row: Row, *, dry_run: bool, force: bool) -> bool:
    print(f"[{row.id}] {row.case} {row.variant} seed {row.seed} -> {rel(row.out)}", flush=True)
    existing = taxonomy_file(row) if row.out.exists() else None
    if existing and not force:
        print(f"  already done ({existing.name}); skipped (use --force to re-run)", flush=True)
        return True
    config = write_config(row) if not dry_run else row.out / "config.yaml"
    log_path = row.out / "run.log"
    started = dt.datetime.now()
    entry: Dict[str, Any] = {"row": row.id, "case": row.case, "variant": row.variant, "seed": row.seed,
                             "started": started.isoformat(timespec="seconds")}
    attempts = 0
    for cmd in commands(row, config):
        ok, n = run_step(cmd, log_path, dry_run)
        attempts += n
        if not ok:
            entry.update(status="failed-run", attempts=attempts, finished=dt.datetime.now().isoformat(timespec="seconds"))
            record(entry)
            return False
    if dry_run:
        for cmd in match_commands(row, row.out / "<taxonomy>.json", config).values():
            print("  $ " + " ".join(cmd))
        return True
    taxonomy = taxonomy_file(row)
    if taxonomy is None:
        entry.update(status="failed-no-taxonomy", attempts=attempts,
                     finished=dt.datetime.now().isoformat(timespec="seconds"))
        record(entry)
        return False
    metrics = json.loads(taxonomy.read_text(encoding="utf-8")).get("run_metrics") or {}
    entry.update(taxonomy=rel(taxonomy), total_tokens=metrics.get("total_tokens", ""),
                 elapsed_seconds=metrics.get("elapsed_seconds", ""))
    status = "ok"
    for view, cmd in match_commands(row, taxonomy, config).items():
        ok, _ = run_step(cmd, log_path, dry_run)
        if not ok:
            status = f"failed-match-{view}"
            break
        found = sorted((row.out / f"match_{view}").glob("*_gt_metrics.json"))
        entry[f"match_{view}"] = rel(found[-1]) if found else ""
    entry.update(status=status, attempts=attempts, finished=dt.datetime.now().isoformat(timespec="seconds"))
    record(entry)
    print(f"  {status}: {entry['total_tokens']} tokens, {entry['elapsed_seconds']} s", flush=True)
    return status == "ok"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("rows", nargs="*", help="row ids, run in the order given (see --list)")
    ap.add_argument("--list", action="store_true", help="list the rows and exit")
    ap.add_argument("--dry-run", action="store_true", help="print the commands; write nothing, call nothing")
    ap.add_argument("--force", action="store_true", help="re-run rows whose folder already holds a taxonomy")
    args = ap.parse_args(argv)
    if args.list or not args.rows:
        for r in MATRIX.values():
            print(f"{r.id:4} {r.case:18} {r.variant:18} seed {r.seed}  {rel(r.config)}")
        return 0
    unknown = [r for r in args.rows if r not in MATRIX]
    if unknown:
        print(f"unknown rows: {', '.join(unknown)} (see --list)", file=sys.stderr)
        return 2
    begun = time.time()
    for rid in args.rows:
        if not run_row(MATRIX[rid], dry_run=args.dry_run, force=args.force):
            print(f"stopped at {rid}; the rows after it were not run. Log: {rel(LOG)}", file=sys.stderr)
            return 1
    print(f"done: {len(args.rows)} rows in {(time.time() - begun) / 60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
