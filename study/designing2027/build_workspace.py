#!/usr/bin/env python3
r"""Build the study's E workspace: the expert ML-workflow decision model, imported as a design space.

The model names each decision by its question ("How to serve model predictions or scores?"). The workspace names
each dimension as a concern instead (``inputs/dimension_names.yaml``: "Model serving") and keeps the question,
word for word, as the dimension's description; ``gt_model.json`` itself is not changed.

The workspace gets a wiki (no quotes, no sampled design points: agents compose points with ``ddspace point``), an
AGENTS.md from ``ddspace agent setup``, and a copy of the input manifest (``inputs/manifest.json``), which the
session runner checks before every E session. The N condition needs no workspace: its work copy is an empty
folder.

The study's sessions ran on the same model with the questions as dimension names. A rebuild has the same dimension
and value ids, but new names and a new run id, so its graph fingerprint differs: ``ddspace rationale check`` on the
study's E files warns ``graph_changed`` (every id still resolves).

Usage::

    python study/designing2027/build_workspace.py --out <folder>     # writes <folder>/E and <folder>/N
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import controls  # noqa: E402

INPUTS = HERE / "inputs"
MANIFEST = "manifest.json"
MODEL_FILE = "gt_model.json"
NAMES_FILE = "dimension_names.yaml"
NAME = "c1-e"                       # the space's name, as in the study's E workspace
USE_CASE = ("The architectural design decisions of the machine learning workflow, from data ingestion and "
            "processing through model building and training to deployment and operation, with the options "
            "for each (Warnett and Zdun's decision model).")


def verify(inputs: Path = INPUTS) -> List[str]:
    """Return the inputs whose content no longer matches the manifest (missing files included)."""
    manifest = json.loads((inputs / MANIFEST).read_text(encoding="utf-8"))
    return [name for name, digest in manifest["files"].items()
            if not (inputs / name).is_file() or controls.sha256(inputs / name) != digest]


def named_model(model: Dict[str, Any], names: Dict[str, str]) -> Dict[str, Any]:
    """A copy of ``model`` whose decisions carry the dimension names of ``names`` (decision id -> name), each with
    its question kept as its description; raise when a decision has no name or a name has no decision."""
    decisions = {d["id"] for d in model.get("decisions") or []}
    missing, unknown = sorted(decisions - set(names)), sorted(set(names) - decisions)
    if missing or unknown:
        raise ValueError(f"dimension names do not match the model's decisions: missing {missing}, unknown {unknown}")
    out = copy.deepcopy(model)
    for d in out["decisions"]:
        d["description"] = d.get("description") or d.get("question") or d.get("name") or ""
        d["name"] = str(names[d["id"]]).strip()
    return out


def _ddspace(cwd: Path, *args: str) -> None:
    """Run the ddspace CLI of this Python environment in ``cwd``; raise with its output on failure."""
    cmd = [sys.executable, "-c", "from delvedspace.cli import app; app()", *args]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ddspace {' '.join(args)} failed in {cwd}:\n{proc.stdout}\n{proc.stderr}")


def build(out: Path, inputs: Path = INPUTS, name: str = NAME) -> Path:
    """(Re)build ``out/E`` (and an empty ``out/N``) from ``inputs``; refuse inputs that differ from their manifest."""
    changed = verify(inputs)
    if changed:
        raise ValueError(f"inputs changed since the manifest was written: {', '.join(changed)}")
    inputs, out = inputs.resolve(), out.resolve()
    ws = out / "E"
    shutil.rmtree(ws, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / "N").mkdir(exist_ok=True)
    _ddspace(out, "init", str(ws), "--yes", "--name", name)
    model = json.loads((inputs / MODEL_FILE).read_text(encoding="utf-8"))
    names = yaml.safe_load((inputs / NAMES_FILE).read_text(encoding="utf-8")) or {}
    with tempfile.TemporaryDirectory() as tmp:
        named = Path(tmp) / MODEL_FILE              # the run file is named after this file's stem, as before
        named.write_text(json.dumps(named_model(model, names), indent=1, ensure_ascii=False), encoding="utf-8")
        _ddspace(ws, "import", str(named), "--kind", "decision-model", "--yes")
    from delvedspace.workspace import Workspace
    workspace = Workspace(ws)
    for key, value in (("design_points", "none"), ("quotes", False), ("source_summaries", False)):
        workspace.set(f"wiki.{key}", value)
    workspace.set("taxonomy.use_case", USE_CASE)
    _ddspace(ws, "wiki", "build", "--yes", "--no-llm")
    _ddspace(ws, "agent", "setup", "--yes")
    shutil.copyfile(inputs / MANIFEST, ws / controls.MANIFEST_COPY)
    return ws


def main() -> None:
    """Build the E workspace under ``--out``."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True, help="folder for E (and an empty N)")
    parser.add_argument("--inputs", type=Path, default=INPUTS)
    args = parser.parse_args()
    print(build(args.out, args.inputs))  # noqa: T201


if __name__ == "__main__":
    main()
