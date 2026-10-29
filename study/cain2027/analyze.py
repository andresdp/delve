#!/usr/bin/env python3
"""Recompute the reported numbers from the recorded results, offline (no API key, no agent, no judge).

Reads ``<results>/scores.json`` (written by ``score.py``) and the hand-checked match labels
(``<results>/labels/*.checked.csv``), and prints:

- per condition, mean ± standard deviation over sessions of the reported metrics, with two-sided Mann-Whitney U
  p-values for N vs M and M vs E (sessions of one brief are not independent, so the p-values are indicative);
- relevant-decision coverage per brief and condition;
- N vs M on relevant-decision coverage: one-sided Mann-Whitney, and paired by brief and repetition (two-sided Wilcoxon);
- the matcher's precision: the share of checked best matches marked correct, overall and per condition, with a
  95% Wilson interval.

Usage::

    python study/cain2027/analyze.py [--results results-<label>]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

from scipy.stats import mannwhitneyu, wilcoxon

import design

CONDITIONS = ("N", "M", "E")
# (label, scores.json key, test N vs M and M vs E)
METRICS = [
    ("ADRs written", "decisions", True),
    ("Relevant-decision coverage (best match)", "relevant_decision_coverage", True),
    ("Relevant-decision coverage, lenient", "relevant_decision_coverage_lenient", True),
    ("Decision coverage (all expert decisions)", "decision_coverage", True),
    ("Requirements fit", "requirements_fit", True),
    ("Decisions fit rests on (fit_decisions)", "fit_decisions", False),
    ("Choices matching no option of their decision", "choices_unmatched", False),
    ("Driver recall", "driver_recall", True),
    ("Alternatives matching an expert option", "alternatives_matched", False),
    ("Decisions listed as left open", "uncovered_listed", True),
    ("Choices with a citation", "grounded_choices", False),
    ("Citations on the choice that refer to the chosen value", "citations_on_choice", False),
    ("Passage citations whose source adopts the chosen value", "supporting_citations", False),
    ("Citations whose source rejects the chosen value", "opposing_citations", False),
    ("ddspace point warnings on the chosen values", "consistency_warnings", False),
    ("Design points checked", "points_explored", False),
]


def values(rows: List[Dict[str, Any]], condition: str, key: str) -> List[float]:
    """The metric's numeric values over the condition's sessions (missing values left out)."""
    return [r[key] for r in rows if r["condition"] == condition and isinstance(r.get(key), (int, float))]


def p_value(a: List[float], b: List[float], alternative: str = "two-sided") -> Optional[float]:
    """Mann-Whitney U p-value, or None when a side is empty or every value is equal."""
    if not a or not b or len(set(a + b)) < 2:
        return None
    return float(mannwhitneyu(a, b, alternative=alternative).pvalue)


def wilson(hits: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def precision(labels: Path) -> Dict[str, Tuple[int, int]]:
    """(correct, checked) best matches per condition and overall, from the ``*.checked.csv`` files."""
    counts: Dict[str, List[int]] = {}
    for path in sorted(labels.glob("*.checked.csv")):
        condition = path.name.split("-")[1]
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mark = (row.get("best match correct (y/n)") or "").strip().lower()
                if not row.get("best_match") or mark not in ("y", "n"):
                    continue
                for group in (condition, "all"):
                    c = counts.setdefault(group, [0, 0])
                    c[0] += mark == "y"
                    c[1] += 1
    return {k: (v[0], v[1]) for k, v in counts.items()}


def _fmt(vals: List[float], spread: bool) -> str:
    if not vals:
        return "-"
    if spread and len(vals) > 1:
        return f"{mean(vals):.2f} ± {stdev(vals):.2f}"
    return f"{mean(vals):.2f}"


def _fmt_p(p: Optional[float]) -> str:
    return "" if p is None else ("< 0.001" if p < 0.0005 else f"{p:.3f}")


def report(results: Path) -> str:
    """The reported numbers as Markdown."""
    rows = json.loads((results / "scores.json").read_text(encoding="utf-8"))["sessions"]
    n = {c: sum(r["condition"] == c for r in rows) for c in CONDITIONS}
    out = [f"# {results.name}: {len(rows)} sessions ({', '.join(f'{c} {n[c]}' for c in CONDITIONS)})", "",
           "Mean ± standard deviation over sessions; p: two-sided Mann-Whitney U over sessions.", "",
           "| Metric | N | M | E | p (N vs M) | p (M vs E) |", "|---|---|---|---|---|---|"]
    for label, key, test in METRICS:
        by = {c: values(rows, c, key) for c in CONDITIONS}
        cells = [_fmt(by[c], test) for c in CONDITIONS]
        tests = [_fmt_p(p_value(by["N"], by["M"])), _fmt_p(p_value(by["M"], by["E"]))] if test else ["", ""]
        out.append(f"| {label} | " + " | ".join(cells + tests) + " |")
    cost = sum(r.get("cost_usd") or 0 for r in rows)
    out += ["", f"Agent cost: ${cost:.2f} for {len(rows)} sessions (tokens priced from `rates.yaml`)."]

    out += ["", "Relevant-decision coverage per brief (N / M / E):", ""]
    for brief in sorted({r["brief"] for r in rows}):
        sub = [r for r in rows if r["brief"] == brief]
        out.append(f"- {brief}: " + " / ".join(_fmt(values(sub, c, "relevant_decision_coverage"), False)
                                                for c in CONDITIONS))

    key = "relevant_decision_coverage"
    pairs = {(r["brief"], r["rep"]): {} for r in rows}
    for r in rows:
        pairs[(r["brief"], r["rep"])][r["condition"]] = r.get(key)
    diffs = [p["M"] - p["N"] for p in pairs.values() if isinstance(p.get("N"), (int, float))
             and isinstance(p.get("M"), (int, float))]
    above, below = sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
    nonzero = [d for d in diffs if d != 0]
    paired = float(wilcoxon(nonzero).pvalue) if nonzero else None
    out += ["", "N vs M on relevant-decision coverage:", "",
            f"- one-sided Mann-Whitney (M > N): p = {_fmt_p(p_value(values(rows, 'M', key), values(rows, 'N', key), 'greater'))}",
            f"- paired by brief and repetition: M above N in {above} of {len(diffs)} pairs, below in {below}, "
            f"tied in {len(diffs) - above - below} (two-sided Wilcoxon p = {_fmt_p(paired)})"]

    checked = precision(results / "labels")
    if checked:
        out += ["", "Matcher precision (hand-checked best matches, `labels/*.checked.csv`):", ""]
        for group in ["all"] + [c for c in CONDITIONS if c in checked]:
            hits, total = checked[group]
            low, high = wilson(hits, total)
            out.append(f"- {group}: {hits}/{total} = {hits / total:.2f} (95% Wilson interval {low:.2f}-{high:.2f})")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--results", default="results",
                        help="results folder in the study folder: results (default) or results-<label>")
    args = parser.parse_args()
    print(report(design.results_folder(args.results)), end="")  # noqa: T201


if __name__ == "__main__":
    main()
