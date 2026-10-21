#!/usr/bin/env python3
"""Crosswalk between a study's paper view and model view of the ground truth.

Every decision and option of either view gets one row with a status:
``paper+model`` (the same element in both views, same id), ``model only`` or
``paper only``. Paper-only elements have ``P``-prefixed ids, so they can never
collide with a model id. The crosswalk is a CSV (``kind, id, name, status,
note``) next to the two views; ``check`` verifies that it covers both views
and agrees with them.

Usage:
  python benchmark/gt_crosswalk.py build <gt folder>   # write gt_crosswalk.csv (keeps notes)
  python benchmark/gt_crosswalk.py check <gt folder>
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

STATUSES = ("paper+model", "model only", "paper only")
FIELDS = ["kind", "id", "name", "status", "note"]
KINDS = (("decision", "decisions"), ("option", "options"))


def _ids(view: dict[str, Any], key: str) -> dict[str, str]:
    return {el["id"]: el["name"] for el in view[key]}


def build_crosswalk(paper: dict[str, Any], model: dict[str, Any],
                    notes: dict[tuple, str] | None = None) -> list[dict[str, str]]:
    """One row per decision and option of either view, matched by id."""
    notes = notes or {}
    rows = []
    for kind, key in KINDS:
        in_paper, in_model = _ids(paper, key), _ids(model, key)
        for el_id in list(in_model) + [i for i in in_paper if i not in in_model]:
            status = ("paper+model" if el_id in in_paper and el_id in in_model
                      else "model only" if el_id in in_model else "paper only")
            rows.append({"kind": kind, "id": el_id, "name": in_model.get(el_id) or in_paper[el_id],
                         "status": status, "note": notes.get((kind, el_id), "")})
    return rows


def check_crosswalk(paper: dict[str, Any], model: dict[str, Any], rows: list[dict[str, str]]) -> list[str]:
    """Errors where the crosswalk misses an element or disagrees with the views."""
    errors = []
    seen = set()
    for kind, key in KINDS:
        in_paper, in_model = _ids(paper, key), _ids(model, key)
        kind_rows = [r for r in rows if r["kind"] == kind]
        listed = {r["id"] for r in kind_rows}
        for el_id in set(in_paper) | set(in_model):
            if el_id not in listed:
                errors.append(f"{kind} '{el_id}' is missing from the crosswalk")
        for row in kind_rows:
            el_id = row["id"]
            if (kind, el_id) in seen:
                errors.append(f"{kind} '{el_id}' is listed twice")
            seen.add((kind, el_id))
            status = row["status"]
            if status not in STATUSES:
                errors.append(f"{kind} '{el_id}': status {status!r} not in {STATUSES}")
                continue
            if status in ("paper+model", "paper only") and el_id not in in_paper:
                errors.append(f"{kind} '{el_id}' is {status} but not in the paper view")
            if status in ("paper+model", "model only") and el_id not in in_model:
                errors.append(f"{kind} '{el_id}' is {status} but not in the model view")
            if status == "model only" and el_id in in_paper:
                errors.append(f"{kind} '{el_id}' is model only but also in the paper view")
            if status == "paper only":
                if el_id in in_model:
                    errors.append(f"{kind} '{el_id}' is paper only but reuses a model id")
                if not el_id.startswith("P"):
                    errors.append(f"{kind} '{el_id}' is paper only; its id must start with 'P'")
    return errors


def read_crosswalk(path: Path) -> list[dict[str, str]]:
    """Read a crosswalk CSV."""
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return [{field: row.get(field, "") or "" for field in FIELDS} for row in csv.DictReader(fh)]


def write_crosswalk(path: Path, rows: list[dict[str, str]]) -> None:
    """Write a crosswalk CSV."""
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _load(folder: Path, name: str) -> dict[str, Any]:
    return json.loads((folder / name).read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2 or args[0] not in ("build", "check"):
        print(__doc__.split("Usage:")[-1].rstrip())
        return 2
    folder = Path(args[1])
    paper, model = _load(folder, "gt_paper.json"), _load(folder, "gt_model.json")
    path = folder / "gt_crosswalk.csv"
    if args[0] == "build":
        notes = {(r["kind"], r["id"]): r["note"] for r in read_crosswalk(path)} if path.exists() else {}
        rows = build_crosswalk(paper, model, notes)
        write_crosswalk(path, rows)
        print(f"wrote {path} ({len(rows)} rows)")
    rows = read_crosswalk(path)
    errors = check_crosswalk(paper, model, rows)
    counts = Counter((row["kind"], row["status"]) for row in rows)
    print(", ".join(f"{n} {kind}s {status}" for (kind, status), n in sorted(counts.items())))
    for msg in errors:
        print(f"error: {msg}")
    print("crosswalk ok" if not errors else f"{len(errors)} crosswalk errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
