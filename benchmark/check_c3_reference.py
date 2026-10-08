#!/usr/bin/env python3
"""Check the C3 reference data against the C3 corpora.

Validates ``benchmark/c3-git-at-scale/passage_systems.csv`` (B7, passage → system
map) and, when present, ``silver_tradeoffs.csv`` (B9, silver trade-off list):

- every C3-raw passage and every curated document is mapped, and no unknown id is;
- system codes come from the fixed vocabulary and ``primary`` is one of ``systems``;
- every trade-off cites at least one existing C3-raw passage, only existing curated
  ids, non-empty quality attributes, and valid ``explicitness`` / ``found_in``.

Lines starting with ``#`` (the status line) are skipped. Rerun after any corpus
rebuild: passage ids are renumbered when the segmentation changes. Exits 1 and
lists the problems when anything is wrong.

Usage::

    python benchmark/check_c3_reference.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

REPO = Path(__file__).resolve().parent.parent
CASE = REPO / "benchmark" / "c3-git-at-scale"
PASSAGES_CSV = REPO / "examples" / "c3-git-at-scale" / "c3-git-at-scale_passages.csv"
CURATED_JSON = REPO / "examples" / "c3-git-at-scale" / "c3-git-at-scale-curated_documents.json"
MAP_CSV = CASE / "passage_systems.csv"
TRADEOFFS_CSV = CASE / "silver_tradeoffs.csv"

SYSTEMS = {"GH-FS", "GOOG-DHT", "GH-SPOKES", "MS-GVFS", "MS-SCALAR", "MS-ADO", "CUR-CONT", "GENERAL"}
EXPLICITNESS = {"stated", "implied"}
FOUND_IN = {"raw", "curated-check"}


def read_rows(path: Path) -> List[Dict[str, str]]:
    """CSV rows as dicts, skipping ``#`` comment lines."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [line for line in f if not line.lstrip().startswith("#")]
    return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(lines)]


def _split(value: str) -> List[str]:
    return [p.strip() for p in (value or "").split(";") if p.strip()]


def check(passage_ids: Set[str], curated_ids: Set[str], map_rows: Iterable[Dict[str, str]],
          tradeoff_rows: Optional[Iterable[Dict[str, str]]]) -> List[str]:
    problems: List[str] = []
    known = {"raw": passage_ids, "curated": curated_ids}
    mapped: Dict[str, Set[str]] = {"raw": set(), "curated": set()}
    for row in map_rows:
        pid, corpus = row.get("passage_id", ""), row.get("corpus", "")
        if corpus not in known:
            problems.append(f"B7 {pid}: corpus must be raw or curated, got {corpus!r}")
            continue
        if pid not in known[corpus]:
            problems.append(f"B7 {pid}: unknown {corpus} id")
        if pid in mapped[corpus]:
            problems.append(f"B7 {pid}: mapped twice")
        mapped[corpus].add(pid)
        systems = _split(row.get("systems", ""))
        if not systems:
            problems.append(f"B7 {pid}: no systems")
        for code in systems:
            if code not in SYSTEMS:
                problems.append(f"B7 {pid}: unknown system code {code}")
        if row.get("primary", "") not in systems:
            problems.append(f"B7 {pid}: primary {row.get('primary')!r} is not one of its systems")
        if not row.get("basis", "").strip():
            problems.append(f"B7 {pid}: empty basis")
    for corpus, ids in known.items():
        for pid in sorted(ids - mapped[corpus]):
            problems.append(f"B7 {pid}: {corpus} id not mapped")

    for row in tradeoff_rows or []:
        tid = row.get("id", "?")
        for field in ("tradeoff", "qa_favoured", "qa_sacrificed"):
            if not row.get(field, "").strip():
                problems.append(f"B9 {tid}: empty {field}")
        for code in _split(row.get("systems", "")) or ["<none>"]:
            if code not in SYSTEMS:
                problems.append(f"B9 {tid}: unknown system code {code}")
        cited = _split(row.get("passage_ids", ""))
        if not cited:
            problems.append(f"B9 {tid}: cites no raw passage")
        for pid in cited:
            if pid not in passage_ids:
                problems.append(f"B9 {tid}: unknown passage {pid}")
        for cid in _split(row.get("curated_ids", "")):
            if cid not in curated_ids:
                problems.append(f"B9 {tid}: unknown curated id {cid}")
        if row.get("explicitness") not in EXPLICITNESS:
            problems.append(f"B9 {tid}: explicitness must be stated or implied")
        if row.get("found_in") not in FOUND_IN:
            problems.append(f"B9 {tid}: found_in must be raw or curated-check")
    return problems


def main() -> int:
    passage_ids = {r["id"] for r in read_rows(PASSAGES_CSV)}
    curated_ids = {e["id"] for e in json.loads(CURATED_JSON.read_text(encoding="utf-8"))}
    tradeoffs = read_rows(TRADEOFFS_CSV) if TRADEOFFS_CSV.exists() else None
    problems = check(passage_ids, curated_ids, read_rows(MAP_CSV), tradeoffs)
    for p in problems:
        print(p)
    status = "B7" + (" + B9" if tradeoffs is not None else " (no B9 file yet)")
    print(f"{status}: {len(problems)} problem(s); {len(passage_ids)} raw passages, {len(curated_ids)} curated documents")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
