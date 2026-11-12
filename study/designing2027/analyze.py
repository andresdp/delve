#!/usr/bin/env python3
r"""Recompute the paper's numbers from the kept rationale files and summaries (offline, no API key).

Prints, per condition, the rows of the paper's table of sessions, then the counts the text quotes: the
unaddressed requirements that are constraints, the trade-offs whose note argues from missing evidence, and the
time per session. Every number is a mean over the condition's sessions unless its label says otherwise.

Usage::

    python study/designing2027/analyze.py [--results results-v2] [--conditions E,N] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent

# A trade-off note that argues from what is missing (an unproven target) rather than from a mechanism. A rough
# keyword match: the paper reports it as such.
EVIDENCE_ABSENCE = re.compile(
    r"unproven|no measured|not measured|not establish|no evidence|does not (prove|show|establish|guarantee|"
    r"demonstrate)|do(es)? not (quantify|state)|unspecified|not demonstrated|no explicit|provide[s]? no|lack|"
    r"needs measurement|not proven|unverified|no .{0,30}evidence", re.I)

ROWS = [   # (key, label in the paper's table, format)
    ("operations", "Operations (query, check, describe)", "{:.0f}"),
    ("points", "Design points examined", "{:.1f}"),
    ("dimensions_per_point", "Dimensions decided per point (search)", "{:.1f}"),
    ("alternatives", "Alternatives (search)", "{:.1f}"),
    ("strong_share", "Steps rated strong (search)", "{:.0%}"),
    ("tradeoffs_per_step", "Trade-offs per step", "{:.1f}"),
    ("values_per_cause", "Values per trade-off cause", "{:.1f}"),
    ("requirements_per_tradeoff", "Requirements per trade-off", "{:.1f}"),
    ("unaddressed", "Unaddressed requirements", "{:.1f}"),
    ("uncovered", "Uncovered decisions (explain)", "{:.1f}"),
    ("shared_values", "Chosen values shared by rep. 1 and 2", "{:.0%}"),
]
TEXT = [
    ("sessions", "Sessions", "{:.0f}"),
    ("minutes", "Minutes per session", "{:.1f}"),
    ("unaddressed_total", "Unaddressed requirements, in all", "{:.0f}"),
    ("unaddressed_constraints", "... of which constraints", "{:.0f}"),
    ("evidence_absence_share", "Trade-offs arguing from missing evidence", "{:.0%}"),
]


def _mean(values: Sequence[float]) -> Optional[float]:
    return statistics.mean(values) if values else None


def _load(results: Path, condition: str) -> List[Dict[str, Any]]:
    """The condition's sessions: each its summary and rationale file, in session order."""
    out = []
    session = re.compile(rf"^.+-{re.escape(condition)}-r\d+$")     # skips copies such as "x-E-r1 2.json"
    for path in sorted(p for p in (results / "rationale").glob(f"*-{condition}-r*.json") if session.match(p.stem)):
        summary = results / "summaries" / path.name
        out.append({"id": path.stem, "doc": json.loads(path.read_text(encoding="utf-8")),
                    "summary": json.loads(summary.read_text(encoding="utf-8")) if summary.is_file() else {}})
    return out


def chosen_values(doc: Dict[str, Any]) -> set:
    """The values the alternatives choose (all points' values when there are no choices)."""
    chosen = {ch.get("value_id") or ch.get("value") for a in doc.get("alternatives") or []
              for ch in a.get("choices") or []} - {None}
    return chosen or {v for p in doc.get("points") or [] for v in p.get("values") or []}


def _case(session_id: str) -> str:
    return session_id.rsplit("-", 2)[0]


def condition_numbers(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The table's rows and the text's counts for one condition's sessions."""
    docs = [s["doc"] for s in sessions]
    search = [d for d in docs if d.get("mode") == "search"]
    explain = [d for d in docs if d.get("mode") == "explain"]
    steps = [st for d in docs for st in d.get("trajectory") or []]
    tradeoffs = [t for st in steps for t in st.get("tradeoffs") or []]
    ratings = [st.get("rating") for d in search for st in d.get("trajectory") or []]
    unaddressed = [u for d in docs for u in d.get("unaddressed") or []]
    by_case: Dict[str, Dict[int, set]] = {}
    for s in sessions:
        rep = int(s["id"].rsplit("-r", 1)[1])
        by_case.setdefault(_case(s["id"]), {})[rep] = chosen_values(s["doc"])
    shared = [len(r[1] & r[2]) / len(r[1] | r[2]) for r in by_case.values() if 1 in r and 2 in r and r[1] | r[2]]
    return {
        "sessions": len(sessions),
        "operations": _mean([sum((s["summary"].get("ddspace_calls") or {}).values()) for s in sessions]),
        "points": _mean([len(d.get("points") or []) for d in docs]),
        "dimensions_per_point": _mean([len(p.get("values") or []) for d in search for p in d.get("points") or []]),
        "alternatives": _mean([len(d.get("alternatives") or []) for d in search]),
        "strong_share": ratings.count("strong") / len(ratings) if ratings else None,
        "tradeoffs_per_step": len(tradeoffs) / len(steps) if steps else None,
        "values_per_cause": _mean([len(t.get("values") or []) for t in tradeoffs]),
        "requirements_per_tradeoff": _mean([len(t.get("gains") or []) + len(t.get("costs") or [])
                                            for t in tradeoffs]),
        "unaddressed": _mean([len(d.get("unaddressed") or []) for d in docs]),
        "uncovered": _mean([len(d.get("uncovered") or []) for d in explain]),
        "shared_values": _mean(shared),
        "minutes": _mean([s["summary"]["seconds"] / 60 for s in sessions if "seconds" in s["summary"]]),
        "unaddressed_total": len(unaddressed),
        "unaddressed_constraints": sum(1 for u in unaddressed if str(u.get("requirement", "")).startswith("C")),
        "evidence_absence_share": (sum(1 for t in tradeoffs if EVIDENCE_ABSENCE.search(t.get("note") or ""))
                                   / len(tradeoffs)) if tradeoffs else None,
    }


def analyze(results: Path, conditions: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    """Every condition's numbers, from ``results/rationale`` and ``results/summaries``."""
    return {c: condition_numbers(_load(results, c)) for c in conditions}


def render(numbers: Dict[str, Dict[str, Any]]) -> str:
    """The numbers as a plain-text table: the paper's table, then the counts the text quotes."""
    conditions = list(numbers)
    width = max(len(label) for _, label, _ in ROWS + TEXT)
    lines = [f"{'':{width}}  " + "  ".join(f"{c:>6}" for c in conditions)]
    for block in (ROWS, TEXT):
        lines.append("")
        for key, label, fmt in block:
            cells = [numbers[c].get(key) for c in conditions]
            lines.append(f"{label:{width}}  " + "  ".join(f"{fmt.format(v) if v is not None else '-':>6}"
                                                          for v in cells))
    return "\n".join(lines)


def main() -> None:
    """Print the numbers for the results folder and conditions on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--results", default="results-v2", help="results folder in this study folder")
    parser.add_argument("--conditions", default="E,N", help="comma-separated conditions")
    parser.add_argument("--json", action="store_true", help="print JSON instead of the table")
    args = parser.parse_args()
    numbers = analyze(HERE / args.results, [c.strip() for c in args.conditions.split(",") if c.strip()])
    print(json.dumps(numbers, indent=2) if args.json else render(numbers))  # noqa: T201


if __name__ == "__main__":
    main()
