#!/usr/bin/env python3
"""Tables for the evaluation runs (docs/plans/2026-10-15-feat-evaluation-runs-plan.md, step 5).

Two commands, both reading the runs that ``benchmark/run_matrix.py`` logged in ``output/evaluation/runs.csv``:

- ``summary`` (no LLM calls): one line per run and one per case and variant (mean, min and max over seeds) with
  the counts, the scoreboard criteria, value exclusivity, the recoding step, cost, and, for C1/C2, the
  ground-truth scores (option P/R/F1, decision F1 strict and lenient, placement) for each view.
- ``stability`` (matching-model calls, or none with ``--matcher-mode embeddings``): the seeds of one case and
  variant matched to each other with the ground-truth matcher. Each pair's reference run is turned into a
  ground-truth folder (its dimensions as decisions, its candidate values as options), then the other run is
  scored against it. Reported per pair: option P/R/F1 and decision F1, strict and lenient.

Outputs go to ``output/evaluation/report/`` (Markdown and CSV).

Usage::

    python benchmark/evaluation_report.py summary
    python benchmark/evaluation_report.py stability --case c3-git-at-scale
    python benchmark/evaluation_report.py stability --case c1-ml-workflow --matcher-mode embeddings
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import itertools
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "output" / "evaluation"
LOG = OUT / "runs.csv"
REPORT = OUT / "report"

GT_VIEWS = ("paper", "model")
TAXONOMY_VIEWS = ("selected", "final")


# ------------------------------------------------------------------- runs

def latest_ok(log: Path = LOG) -> List[Dict[str, str]]:
    """The last successful entry of every row, in the order the rows first appear in the log."""
    rows: Dict[str, Dict[str, str]] = {}
    if not log.exists():
        return []
    with log.open(encoding="utf-8") as fh:
        for entry in csv.DictReader(fh):
            if entry.get("status") == "ok":
                rows.pop(entry["row"], None)        # keep the latest, at the position of its last run
                rows[entry["row"]] = entry
    return list(rows.values())


def _abs(path: str) -> Optional[Path]:
    if not path:
        return None
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def run_record(entry: Dict[str, str]) -> Dict[str, Any]:
    """The numbers of one run: counts, scoreboard, recoding, cost and ground-truth scores."""
    data = json.loads(_abs(entry["taxonomy"]).read_text(encoding="utf-8"))
    selected = data.get("selected_clusters") or (data.get("iterations") or [{}])[-1].get("clusters") or []
    values = [v for c in selected for v in c.get("values") or []]
    rec: Dict[str, Any] = {
        "row": entry["row"], "case": entry["case"], "variant": entry["variant"], "seed": int(entry["seed"]),
        "dimensions": len(selected), "values": len(values),
        "candidates": sum(1 for v in values if v.get("status") in ("accepted", "rejected", "both")),
        "outcomes": sum(1 for v in values if v.get("status") == "outcome"),
        "iterations": len(data.get("iterations") or []),
        "dropped_dimensions": len(data.get("dropped_dimensions") or []),
        "total_tokens": (data.get("run_metrics") or {}).get("total_tokens"),
        "minutes": round(((data.get("run_metrics") or {}).get("elapsed_seconds") or 0) / 60, 1),
    }
    evaluation = data.get("evaluation") or {}
    rec["overall"] = evaluation.get("overall")
    for crit in evaluation.get("criteria") or []:
        if isinstance(crit, dict) and crit.get("evaluated", True):
            rec[f"crit:{crit.get('name')}"] = crit.get("score")
    recoding = next((op for op in data.get("operation_log") or [] if op.get("node") == "value_recoding"), None)
    if recoding:
        rec.update({"exclusivity_before_recoding": recoding.get("before"),
                    "exclusivity_after_recoding": recoding.get("after"),
                    "recoded": len(recoding.get("recoded") or [])})     # the recoded dimensions
    for view in TAXONOMY_VIEWS:
        path = _abs(entry.get(f"match_{view}", ""))
        if not path or not path.exists():
            continue
        metrics = json.loads(path.read_text(encoding="utf-8"))
        for gt_view in GT_VIEWS:
            m = metrics.get(gt_view)
            if not m:
                continue
            key = f"{view}/{gt_view}"
            rec[f"{key}:option_p"] = m["option"]["precision"]
            rec[f"{key}:option_r"] = m["option"]["recall"]
            rec[f"{key}:option_f1"] = m["option"]["f1"]
            rec[f"{key}:decision_f1_strict"] = m["decision"]["strict"]["f1"]
            rec[f"{key}:decision_f1_lenient"] = m["decision"]["lenient"]["f1"]
            rec[f"{key}:placement"] = m["placement"]["accuracy"]
    return rec


def aggregate(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mean, min and max over seeds of every numeric field, per case and variant."""
    groups: Dict[tuple, List[Dict[str, Any]]] = {}
    for r in records:
        groups.setdefault((r["case"], r["variant"]), []).append(r)
    out = []
    for (case, variant), runs in groups.items():
        row: Dict[str, Any] = {"case": case, "variant": variant, "n": len(runs),
                               "seeds": " ".join(str(r["seed"]) for r in runs)}
        keys = dict.fromkeys(k for r in runs for k in r if k not in ("row", "case", "variant", "seed"))
        for k in keys:
            nums = [r[k] for r in runs if isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool)]
            if not nums:
                continue
            row[k] = {"mean": round(statistics.fmean(nums), 4), "min": min(nums), "max": max(nums),
                      "n": len(nums)}
        out.append(row)
    return out


def _fmt(cell: Any) -> str:
    if isinstance(cell, dict):
        if cell["n"] == 1 or cell["min"] == cell["max"]:
            return _num(cell["mean"])
        return f"{_num(cell['mean'])} [{_num(cell['min'])}–{_num(cell['max'])}]"
    return _num(cell) if isinstance(cell, (int, float)) else str(cell if cell is not None else "")


def _num(x: Any) -> str:
    if isinstance(x, float) and x.is_integer() and (x == 0 or abs(x) >= 1):
        x = int(x)
    if isinstance(x, float):
        return f"{x:.2f}" if abs(x) < 100 else f"{x:,.0f}"
    return f"{x:,}" if isinstance(x, int) else str(x)


def markdown_table(rows: List[Dict[str, Any]], columns: List[tuple]) -> str:
    """``columns`` is a list of (header, key); missing keys print as empty cells."""
    lines = ["| " + " | ".join(h for h, _ in columns) + " |", "|" + "---|" * len(columns)]
    for r in rows:
        lines.append("| " + " | ".join(_fmt(r.get(k)) for _, k in columns) + " |")
    return "\n".join(lines)


SUMMARY_COLUMNS = [
    ("Case", "case"), ("Variant", "variant"), ("Seeds", "seeds"), ("Dims", "dimensions"),
    ("Values", "values"), ("Overall", "overall"), ("Exclusivity", "crit:Value exclusivity"),
    ("Tokens", "total_tokens"), ("Min", "minutes"),
]
GT_COLUMNS = [
    ("Case", "case"), ("Variant", "variant"), ("Seeds", "seeds"),
    ("Option P", "selected/{v}:option_p"), ("Option R", "selected/{v}:option_r"),
    ("Option F1", "selected/{v}:option_f1"), ("Decision F1 strict", "selected/{v}:decision_f1_strict"),
    ("Decision F1 lenient", "selected/{v}:decision_f1_lenient"), ("Placement", "selected/{v}:placement"),
    ("Option F1 (final)", "final/{v}:option_f1"), ("Decision F1 lenient (final)", "final/{v}:decision_f1_lenient"),
]


def write_summary(records: List[Dict[str, Any]], out: Path = REPORT) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    groups = aggregate(records)
    criteria = sorted({k for r in records for k in r if k.startswith("crit:")})
    parts = ["# Evaluation runs: summary", "",
             f"{len(records)} runs from `{LOG.relative_to(ROOT)}`. Cells are the mean over seeds, with "
             "[min–max] when they differ. Ground-truth scores use the `selected` view unless marked final.", "",
             "## Runs per case and variant", "", markdown_table(groups, SUMMARY_COLUMNS), ""]
    matched = [g for g in groups if any(k.startswith("selected/") for k in g)]
    for gt_view in GT_VIEWS:
        cols = [(h, k.format(v=gt_view)) for h, k in GT_COLUMNS]
        if any(c[1] in g for g in matched for c in cols[3:]):
            parts += [f"## Ground truth: {gt_view} view", "", markdown_table(matched, cols), ""]
    parts += ["## Scoreboard criteria", "",
              markdown_table(groups, [("Case", "case"), ("Variant", "variant")]
                             + [(c[5:], c) for c in criteria] + [("Overall", "overall")]), "",
              "## Recoding", "",
              markdown_table(groups, [("Case", "case"), ("Variant", "variant"),
                                      ("Exclusivity before", "exclusivity_before_recoding"),
                                      ("After", "exclusivity_after_recoding"), ("Recoded", "recoded")]), "",
              "## Every run", "",
              markdown_table(records, [("Row", "row")] + SUMMARY_COLUMNS[:2] + [("Seed", "seed")]
                             + SUMMARY_COLUMNS[3:] + [("Option F1 paper", "selected/paper:option_f1"),
                                                      ("Option F1 model", "selected/model:option_f1")]), ""]
    md = out / "summary.md"
    md.write_text("\n".join(parts), encoding="utf-8")
    keys = list(dict.fromkeys(k for r in records for k in r))
    with (out / "runs_flat.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    return md


# -------------------------------------------------------------- stability

def _gt_id(prefix: str, raw: Any) -> str:
    return prefix + re.sub(r"[^A-Za-z0-9_.\-]", "_", str(raw))


def taxonomy_to_gt(clusters: List[Dict[str, Any]], study: str, source: str,
                   include_outcomes: bool = False) -> Dict[str, Any]:
    """A run's design space in the ground-truth format (view ``model``): dimensions become decisions, candidate
    values become options. Outcomes are left out unless the matcher counts them (``matcher.include_outcomes``)."""
    decisions, options = [], []
    for c in clusters:
        dec_id = _gt_id("D", c.get("id"))
        decisions.append({"id": dec_id, "name": c.get("name") or dec_id, "question": c.get("description", ""),
                          "decision_type": "unspecified", "description": c.get("description", ""),
                          "description_source": "", "source": f"{source}#dimension {c.get('id')}"})
        for v in c.get("values") or []:
            if v.get("status") == "outcome" and not include_outcomes:
                continue
            options.append({"id": _gt_id("V", f"{c.get('id')}_{v.get('id')}"), "name": v.get("label") or "?",
                            "decision_ids": [dec_id], "description": v.get("description", ""),
                            "description_source": "", "source": f"{source}#value {v.get('id')}"})
    return {"format_version": 1, "study": study, "view": "model",
            "provenance": {"kind": "run as reference", "taxonomy": source},
            "decisions": decisions, "options": options, "forces": [], "decision_forces": [], "impacts": [],
            "decision_links": [], "solution_links": []}


async def match_pair(reference: Dict[str, str], other: Dict[str, str], *, view: str, mode: Optional[str],
                     out: Path) -> Dict[str, Any]:
    """Score ``other`` against ``reference`` turned into a ground-truth folder."""
    from taxonomy_generator.evaluation.gt_match import run_match
    from taxonomy_generator.settings import load_settings
    from taxonomy_generator.utils import load_seed_taxonomy

    ref_path = _abs(reference["taxonomy"])
    settings = load_settings(str(_abs(reference["taxonomy"]).parent / "config.yaml"))
    clusters = load_seed_taxonomy(str(ref_path), view=view)
    gt_dir = out / f"ref_{reference['row']}_{view}"
    gt_dir.mkdir(parents=True, exist_ok=True)
    gt = taxonomy_to_gt(clusters, reference["case"], ref_path.name, settings.matcher.include_outcomes)
    (gt_dir / "gt_model.json").write_text(json.dumps(gt, indent=1, ensure_ascii=False), encoding="utf-8")
    result = await run_match(str(_abs(other["taxonomy"])), str(gt_dir), settings, mode_override=mode,
                             out_dir=str(out / f"{other['row']}_vs_{reference['row']}_{view}"), view=view)
    m = result["metrics"]["model"]
    return {"reference": reference["row"], "other": other["row"],
            "seeds": f"{reference['seed']} vs {other['seed']}", "view": view, "mode": result["settings"]["mode"],
            "reference_values": len(gt["options"]), "other_values": result["settings"]["system_values"],
            "option_p": m["option"]["precision"], "option_r": m["option"]["recall"], "option_f1": m["option"]["f1"],
            "decision_f1_strict": m["decision"]["strict"]["f1"],
            "decision_f1_lenient": m["decision"]["lenient"]["f1"]}


def stability(case: str, variant: str, view: str, mode: Optional[str], out: Path = REPORT) -> Path:
    runs = [e for e in latest_ok() if e["case"] == case and e["variant"] == variant]
    if len(runs) < 2:
        raise SystemExit(f"stability needs at least two successful runs of {case} {variant}; found {len(runs)}")
    folder = out / f"stability_{case}_{variant}"
    async def all_pairs() -> List[Dict[str, Any]]:       # one event loop, so cached clients close cleanly
        return [await match_pair(a, b, view=view, mode=mode, out=folder)
                for a, b in itertools.combinations(runs, 2)]

    pairs = asyncio.run(all_pairs())
    mean = {k: round(statistics.fmean(p[k] for p in pairs), 4)
            for k in ("option_p", "option_r", "option_f1", "decision_f1_strict", "decision_f1_lenient")}
    cols = [("Pair", "seeds"), ("Ref. values", "reference_values"), ("Other values", "other_values"),
            ("Option P", "option_p"), ("Option R", "option_r"), ("Option F1", "option_f1"),
            ("Decision F1 strict", "decision_f1_strict"), ("Decision F1 lenient", "decision_f1_lenient")]
    md = folder / "stability.md"
    md.write_text("\n".join([
        f"# Seed stability: {case} {variant} ({view} view)", "",
        f"Each pair: the second run scored against the first, used as the reference, with the ground-truth "
        f"matcher (mode {pairs[0]['mode']}). Mean option F1 {mean['option_f1']:.2f}; mean decision F1 "
        f"{mean['decision_f1_strict']:.2f} strict, {mean['decision_f1_lenient']:.2f} lenient.", "",
        markdown_table(pairs + [{"seeds": "mean", **mean}], cols), ""]), encoding="utf-8")
    (folder / "stability.json").write_text(json.dumps({"pairs": pairs, "mean": mean}, indent=2), encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("summary", help="tables over the logged runs (no LLM calls)")
    st = sub.add_parser("stability", help="match one case's seeds to each other")
    st.add_argument("--case", required=True)
    st.add_argument("--variant", default="full")
    st.add_argument("--view", choices=TAXONOMY_VIEWS, default="selected")
    st.add_argument("--matcher-mode", choices=["judge", "embeddings"], default=None,
                    help="default: the run config's matcher.mode; 'embeddings' makes no LLM calls")
    args = ap.parse_args(argv)
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    if args.command == "summary":
        records = [run_record(e) for e in latest_ok()]
        if not records:
            print(f"no successful runs in {LOG}", file=sys.stderr)
            return 1
        print(f"-> {write_summary(records)}")
    else:
        print(f"-> {stability(args.case, args.variant, args.view, args.matcher_mode)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
