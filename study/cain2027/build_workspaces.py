#!/usr/bin/env python3
r"""Build the three study workspaces (N, M, E) from the tracked inputs in ``study/cain2027/inputs/``.

- ``N``: an empty folder; the session runner adds the brief.
- ``M``: the C1 seed-42 mined design space, imported as a run (no corpus, so no quotes ship).
- ``E``: the C1 expert decision model, imported without forces and impacts.

Both M and E get a wiki without sampled design points (agents compose points with ``ddspace point``), an
AGENTS.md from ``ddspace agent setup``, and a copy of the input manifest so a session can check where its
workspace came from.

Usage::

    # once, from the evaluation run (writes the tracked inputs)
    python study/cain2027/build_workspaces.py prepare \\
        --run output/evaluation/c1-ml-workflow/full_s42 \\
        --model benchmark/c1-ml-workflow/gt/gt_model.json \\
        --sources benchmark/c1-ml-workflow/sources.csv
    # any time, from a clean checkout
    python study/cain2027/build_workspaces.py build --out <folder>
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design  # noqa: E402

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
MANIFEST = "manifest.json"
MANIFEST_COPY = design.MANIFEST_COPY
MODEL_FILE = "gt_model.json"
# What the wiki and the query layer read from a run taxonomy; the rest is pipeline history (2.8 MB on C1).
KEEP = ("taxonomy_name", "run_metrics", "selected_clusters", "dropped_dimensions", "evaluation")
_ABSOLUTE = re.compile(r"(^|[\s'\"=])(/\w|[A-Za-z]:\\)")   # an absolute path value (not a URL)


def _taxonomy(folder: Path) -> Path:
    from delvedspace.runs import is_taxonomy_name
    found = sorted(p for p in folder.glob("*_taxonomy_*.json") if is_taxonomy_name(p.name))
    if len(found) != 1:
        raise ValueError(f"{folder}: expected one *_taxonomy_*.json, found {len(found)}")
    return found[0]


def trim(taxonomy: Dict) -> Dict:
    """Keep the design space (selected clusters, last iteration, metrics, critic scores); drop the history."""
    out = {k: taxonomy[k] for k in KEEP if k in taxonomy}
    out["iterations"] = (taxonomy.get("iterations") or [])[-1:]
    return out


def prepare(run: Path, model: Path, sources: Path, out: Path = INPUTS) -> Path:
    """Write the tracked inputs (trimmed taxonomy, config, sources, model) and their manifest into ``out``."""
    config = (run / "config.yaml").read_text(encoding="utf-8")
    if _ABSOLUTE.search(config):
        raise ValueError(f"{run / 'config.yaml'} contains an absolute path; remove it before tracking the config")
    out.mkdir(parents=True, exist_ok=True)
    taxonomy_path = _taxonomy(run)
    taxonomy = trim(json.loads(taxonomy_path.read_text(encoding="utf-8")))
    (out / taxonomy_path.name).write_text(json.dumps(taxonomy, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "config.yaml").write_text(config, encoding="utf-8")
    shutil.copyfile(sources, out / "sources.csv")
    shutil.copyfile(model, out / MODEL_FILE)
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != MANIFEST)
    manifest = {"source_run": run.name, "taxonomy": taxonomy_path.name,
                "files": {p.name: design.sha256(p) for p in files}}
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return out


def verify(inputs: Path = INPUTS) -> List[str]:
    """Return the inputs whose content no longer matches the manifest (missing files included)."""
    manifest = json.loads((inputs / MANIFEST).read_text(encoding="utf-8"))
    return [name for name, digest in manifest["files"].items()
            if not (inputs / name).is_file() or design.sha256(inputs / name) != digest]


def _ddspace(cwd: Path, *args: str) -> None:
    """Run the ddspace CLI of this Python environment in ``cwd``; raise with its output on failure."""
    cmd = [sys.executable, "-c", "from delvedspace.cli import app; app()", *args]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ddspace {' '.join(args)} failed in {cwd}:\n{proc.stdout}\n{proc.stderr}")


def _set_wiki(ws: Path, **values) -> None:
    from delvedspace.workspace import Workspace
    w = Workspace(ws)
    for key, value in values.items():
        w.set(f"wiki.{key}", value)


def _workspace(root: Path, name: str, inputs: Path, import_args: List[str]) -> Path:
    ws = root / name
    _ddspace(root, "init", str(ws), "--yes", "--name", f"c1-{name.lower()}", "--from-config",
             str(inputs / "config.yaml"))
    _ddspace(ws, "import", *import_args, "--yes")
    _set_wiki(ws, design_points="none", quotes=False, source_summaries=False)
    _ddspace(ws, "wiki", "build", "--yes", "--no-llm")
    _ddspace(ws, "agent", "setup", "--yes")
    shutil.copyfile(inputs / MANIFEST, ws / MANIFEST_COPY)
    return ws


def build(inputs: Path = INPUTS, out: Path = HERE / "workspaces") -> Dict[str, Path]:
    """(Re)build N, M and E under ``out`` from ``inputs``; refuse inputs that differ from their manifest."""
    changed = verify(inputs)
    if changed:
        raise ValueError(f"inputs changed since the manifest was written: {', '.join(changed)}")
    inputs, out = inputs.resolve(), out.resolve()
    for name in ("N", "M", "E"):
        shutil.rmtree(out / name, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / "N").mkdir()
    manifest = json.loads((inputs / MANIFEST).read_text(encoding="utf-8"))
    m = _workspace(out, "M", inputs, [str(inputs / manifest["taxonomy"]), "--kind", "run",
                                      "--sources", str(inputs / "sources.csv")])
    e = _workspace(out, "E", inputs, [str(inputs / MODEL_FILE), "--kind", "decision-model"])
    return {"N": out / "N", "M": m, "E": e}


def main() -> None:
    """Prepare the inputs or build the workspaces, as the command line says."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="write the tracked inputs from an evaluation run")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--out", type=Path, default=INPUTS)
    b = sub.add_parser("build", help="build the N, M and E workspaces")
    b.add_argument("--inputs", type=Path, default=INPUTS)
    b.add_argument("--out", type=Path, default=HERE / "workspaces")
    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare(args.run, args.model, args.sources, args.out))  # noqa: T201
    else:
        for name, path in build(args.inputs, args.out).items():
            print(f"{name}: {path}")  # noqa: T201


if __name__ == "__main__":
    main()
