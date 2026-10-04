#!/usr/bin/env python3
"""Ground-truth format for the expert design spaces (C1, C2) and its validator.

One JSON file holds one *view* of a study (``model``: the authors' full model;
``paper``: the design space as the paper reports it). Every element has a
stable ``id`` (letters, digits, ``_``, ``.``, ``-``; unique across all element
kinds of the file) and a ``source`` reference (file and line, or page/table).

```
{
  "format_version": 1,
  "study": "c2-rl-monitoring",
  "view": "model" | "paper",
  "provenance": {...},                      # free-form: package, files, hashes, notes
  "decisions": [{"id", "name", "question", "decision_type", "description",
                 "description_source", "source"}],
  "options": [{"id", "name", "decision_ids": [...], "description",
               "description_source", "source", "unattached"?: true}],
  "forces": [{"id", "name", "description", "description_source", "source"}],
  "decision_forces": [{"decision_id", "force_id", "text", "source"}],
  "impacts": [{"option_id", "force_id", "impact", "source"}],
  "decision_links": [{"from", "to", "stereotypes": [...], "label", "source"}],
  "solution_links": [{"from", "to", "stereotypes": [...], "label", "source"}]   # optional
}
```

- ``decision_type`` is ``single``, ``multiple`` or ``unspecified`` (a warning).
- An option listed under several decisions keeps one id. An option under no
  decision must be marked ``"unattached": true``; it is kept for traceability
  and excluded from scoring.
- ``description_source`` says whose text the description is: ``model`` (a
  tagged value in the model), ``model_positional`` (the model's positional
  ``option_name`` argument), ``memo``, ``paper``, or ``benchmark_authors`` (a
  sentence written by the benchmark authors). Descriptions are never generated
  by an LLM. An empty description is a warning.
- ``decision_forces`` holds the per-decision text of a force (its driver text
  differs from decision to decision).
- ``solution_links`` (optional) are links with an option at one end: an option
  that makes a next decision relevant, or a dependency between options (e.g.
  "Can Use", "Requires"). They are kept for traceability and not scored.
- Impacts and link stereotypes use the vocabularies of the C2 guidance
  metamodel (CodeableModels), listed below.

Usage: ``python benchmark/gt_format.py benchmark/*/gt/gt_*.json``
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1
VIEWS = ("model", "paper")
DECISION_TYPES = ("single", "multiple", "unspecified")
IMPACTS = ("++", "+", "o", "-", "--", "+/-")
DESCRIPTION_SOURCES = ("", "model", "model_positional", "memo", "paper", "benchmark_authors")

# Stereotypes of decision-to-decision links in the guidance metamodel: the
# "next decision" relation types and the design-solution dependency types.
NEXT_DECISION_STEREOTYPES = (
    "Mandatory Next", "Optional Next", "Next", "Consider If Not Decided Yet",
    "Feeds Into Via Trigger", "Complements But Limited By", "Complements", "Constrains",
    "Tense Interaction Requires Separation", "Enables", "Can Be Combined With",
)
DEPENDENCY_STEREOTYPES = (
    "Requires", "Uses", "Can Use", "Can Be Combined With", "Can be Realized By", "Has Variant",
    "Extension", "Is-a", "Realizes", "Includes", "Can Include", "Alternative To", "Rules Out",
    "Influences", "Leads To", "Enables",
)
LINK_STEREOTYPES = tuple(dict.fromkeys(NEXT_DECISION_STEREOTYPES + DEPENDENCY_STEREOTYPES))

ELEMENT_LISTS = ("decisions", "options", "forces")
RELATION_LISTS = ("decision_forces", "impacts", "decision_links")
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]*$")


class GroundTruthError(ValueError):
    """A ground-truth file violates the format."""


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Check a ground-truth view; return ``(errors, warnings)`` as readable messages."""
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("format_version") != FORMAT_VERSION:
        errors.append(f"format_version must be {FORMAT_VERSION}, got {data.get('format_version')!r}")
    if not data.get("study"):
        errors.append("study is missing")
    if data.get("view") not in VIEWS:
        errors.append(f"view must be one of {VIEWS}, got {data.get('view')!r}")
    missing = [key for key in ELEMENT_LISTS + RELATION_LISTS if not isinstance(data.get(key), list)]
    if not isinstance(data.get("solution_links", []), list):
        missing.append("solution_links")
    for key in missing:
        errors.append(f"{key} must be a list")
    if missing:
        return errors, warnings

    # Ids: well-formed and unique across every element kind.
    seen: dict[str, str] = {}
    ids: dict[str, set] = {key: set() for key in ELEMENT_LISTS}
    for key in ELEMENT_LISTS:
        for i, item in enumerate(data[key]):
            loc = f"{key}[{i}]"
            item_id = item.get("id")
            if not isinstance(item_id, str) or not ID_RE.match(item_id):
                errors.append(f"{loc}: malformed id {item_id!r}")
                continue
            if item_id in seen:
                errors.append(f"duplicate id '{item_id}': {seen[item_id]} and {loc}")
            else:
                seen[item_id] = loc
            ids[key].add(item_id)
            if not str(item.get("name", "")).strip():
                errors.append(f"{loc}: name is empty")
            if not str(item.get("source", "")).strip():
                errors.append(f"{loc}: source reference is empty")
            desc_source = item.get("description_source", "")
            if desc_source not in DESCRIPTION_SOURCES:
                errors.append(f"{loc}: description_source {desc_source!r} not in {DESCRIPTION_SOURCES}")
            if key != "forces" and not str(item.get("description", "")).strip():
                warnings.append(f"{loc} ({item_id}): empty description")

    decisions, options, forces = ids["decisions"], ids["options"], ids["forces"]

    for i, dec in enumerate(data["decisions"]):
        dtype = dec.get("decision_type")
        if dtype not in DECISION_TYPES:
            errors.append(f"decisions[{i}]: decision_type {dtype!r} not in {DECISION_TYPES}")
        elif dtype == "unspecified":
            warnings.append(f"decisions[{i}] ({dec.get('id')}): decision type unspecified")

    for i, opt in enumerate(data["options"]):
        loc = f"options[{i}]"
        dec_ids = opt.get("decision_ids")
        if not isinstance(dec_ids, list):
            errors.append(f"{loc}: decision_ids must be a list")
            continue
        for dec_id in dec_ids:
            if dec_id not in decisions:
                errors.append(f"{loc}: unknown decision '{dec_id}'")
        if len(set(dec_ids)) != len(dec_ids):
            errors.append(f"{loc}: decision_ids repeats a decision")
        if not dec_ids and not opt.get("unattached"):
            errors.append(f"{loc}: no decision_ids; mark the option \"unattached\": true")
        elif not dec_ids:
            warnings.append(f"{loc} ({opt.get('id')}): unattached option, excluded from scoring")
        elif opt.get("unattached"):
            errors.append(f"{loc}: marked unattached but has decision_ids")

    for i, rec in enumerate(data["decision_forces"]):
        loc = f"decision_forces[{i}]"
        if rec.get("decision_id") not in decisions:
            errors.append(f"{loc}: unknown decision '{rec.get('decision_id')}'")
        if rec.get("force_id") not in forces:
            errors.append(f"{loc}: unknown force '{rec.get('force_id')}'")
        if not str(rec.get("source", "")).strip():
            errors.append(f"{loc}: source reference is empty")

    for i, rec in enumerate(data["impacts"]):
        loc = f"impacts[{i}]"
        if rec.get("option_id") not in options:
            errors.append(f"{loc}: unknown option '{rec.get('option_id')}'")
        if rec.get("force_id") not in forces:
            errors.append(f"{loc}: unknown force '{rec.get('force_id')}'")
        if rec.get("impact") not in IMPACTS:
            errors.append(f"{loc}: impact {rec.get('impact')!r} not in {IMPACTS}")
        if not str(rec.get("source", "")).strip():
            errors.append(f"{loc}: source reference is empty")

    links = [("decision_links", i, lk, decisions, "decision") for i, lk in enumerate(data["decision_links"])]
    links += [("solution_links", i, lk, decisions | options, "decision or option")
              for i, lk in enumerate(data.get("solution_links", []))]
    for key, i, link, known, what in links:
        loc = f"{key}[{i}]"
        for end in ("from", "to"):
            if link.get(end) not in known:
                errors.append(f"{loc}: unknown {what} '{link.get(end)}' ({end})")
        stereotypes = link.get("stereotypes")
        if not isinstance(stereotypes, list) or not stereotypes:
            errors.append(f"{loc}: stereotypes must be a non-empty list")
        else:
            for st in stereotypes:
                if st not in LINK_STEREOTYPES:
                    errors.append(f"{loc}: link stereotype {st!r} not in the guidance metamodel")
        if not str(link.get("source", "")).strip():
            errors.append(f"{loc}: source reference is empty")

    return errors, warnings


def load_ground_truth(path: Path | str) -> tuple[dict[str, Any], list[str]]:
    """Load and validate a ground-truth view; raise :class:`GroundTruthError` on errors."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = validate(data)
    if errors:
        raise GroundTruthError(f"{path}: " + "; ".join(errors))
    return data, warnings


def main(argv: Sequence[str] | None = None) -> int:
    """Validate each file given; print errors and warnings; return 1 if any file has errors."""
    paths = list(sys.argv[1:] if argv is None else argv)
    if not paths:
        print(__doc__.split("Usage: ")[-1].strip())
        return 2
    failed = False
    for name in paths:
        try:
            data = json.loads(Path(name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{name}: cannot read: {exc}")
            failed = True
            continue
        errors, warnings = validate(data)
        counts = ", ".join(f"{len(data.get(k) or [])} {k}" for k in ELEMENT_LISTS + RELATION_LISTS)
        print(f"{name}: {'INVALID' if errors else 'ok'} ({counts}; {len(warnings)} warnings)")
        for msg in errors:
            print(f"  error: {msg}")
        for msg in warnings:
            print(f"  warning: {msg}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
