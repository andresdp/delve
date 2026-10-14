"""Pipeline runs in a workspace: run folders, the current-run pointer, and the call into the pipeline.

Every ``ddspace mine`` / ``update`` creates ``runs/<timestamp>/`` and runs the pipeline
(``taxonomy_generator.pipeline_cli``) in a subprocess with the workspace as working folder, so the
workspace ``.env`` and ``ddspace.yaml`` apply. ``run.json`` in the run folder records what the run was
(kind, seed run, feedback, sources) for later updates and the wiki's change log.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from delvedspace.workspace import Workspace, WorkspaceError

RUN_FILE = "run.json"
# Rough cost per passage, measured on the C3 sample (48 passages, critic on, batch 10):
# 1.46M tokens and 22 minutes. Used only until the workspace has a run of its own.
TOKENS_PER_PASSAGE = 30_000
SECONDS_PER_PASSAGE = 28
_ARTIFACT_MARKERS = ("_design_points", "_match", "_metrics", "_vectors")


@dataclass
class Run:
    """What one run was; stored as ``runs/<id>/run.json``."""

    id: str
    kind: str                                  # mine | update-feedback | update-test
    started_at: str
    status: str = "running"                    # running | ok | failed
    finished_at: Optional[str] = None
    seed_run: Optional[str] = None             # the run this one starts from (updates)
    feedback: Optional[str] = None
    source_ids: List[str] = field(default_factory=list)    # sources whose passages the design space covers
    new_source_ids: List[str] = field(default_factory=list)  # test updates: the sources this run added
    passages: int = 0                          # passages the pipeline read in this run
    taxonomy: Optional[str] = None             # taxonomy JSON file name in the run folder
    argv: List[str] = field(default_factory=list)


def now_id() -> str:
    """Return a run id (a timestamp, which sorts by time)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def new_run_dir(ws: Workspace) -> Path:
    """Create and return an empty ``runs/<timestamp>/`` folder (unique even within one second)."""
    base = now_id()
    for n in range(100):
        run_dir = ws.runs_dir / (base if n == 0 else f"{base}_{n}")
        if not run_dir.exists():
            run_dir.mkdir(parents=True)
            return run_dir
    raise WorkspaceError("Could not create a run folder")


def save(run_dir: Path, run: Run) -> None:
    """Write ``run.json``."""
    (run_dir / RUN_FILE).write_text(json.dumps(asdict(run), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(run_dir: Path) -> Optional[Run]:
    """Read ``run.json`` (None when the folder has none)."""
    path = run_dir / RUN_FILE
    if not path.is_file():
        return None
    return Run(**json.loads(path.read_text(encoding="utf-8")))


def find_taxonomy(run_dir: Path) -> Optional[Path]:
    """Return the taxonomy JSON a pipeline run wrote into ``run_dir`` (the newest, if several)."""
    found = [p for p in run_dir.glob("*_taxonomy_*.json") if not any(m in p.stem for m in _ARTIFACT_MARKERS)]
    return max(found, key=lambda p: p.name) if found else None


def current_run_dir(ws: Workspace) -> Optional[Path]:
    """Return the folder of the current run (``workspace.current_run``), or None before the first run."""
    value = (ws.config().get("workspace") or {}).get("current_run")
    if not value:
        return None
    run_dir = (ws.root / str(value)).resolve()
    if not run_dir.is_dir():
        raise WorkspaceError(f"The current run {value} is missing. Set workspace.current_run in ddspace.yaml "
                             "to an existing folder under runs/, or run `ddspace mine --fresh`.")
    return run_dir


def current_taxonomy(ws: Workspace) -> Path:
    """Return the current run's taxonomy JSON, or explain how to get one."""
    run_dir = current_run_dir(ws)
    if run_dir is None:
        raise WorkspaceError("No design space yet. Run `ddspace mine` first.")
    taxonomy = find_taxonomy(run_dir)
    if taxonomy is None:
        raise WorkspaceError(f"The current run {run_dir.name} has no taxonomy JSON.")
    return taxonomy


def relative(ws: Workspace, path: Path) -> str:
    """Return ``path`` relative to the workspace root, with forward slashes."""
    return path.resolve().relative_to(ws.root).as_posix()


def pipeline_command(argv: List[str]) -> List[str]:
    """Return the command that runs the pipeline with ``argv`` in this Python environment."""
    return [sys.executable, "-m", "taxonomy_generator.pipeline_cli", *argv]


def run_pipeline(ws: Workspace, argv: List[str]) -> int:
    """Run the pipeline in the workspace folder; return its exit code (output goes to the terminal)."""
    return subprocess.run(pipeline_command(argv), cwd=ws.root).returncode


@dataclass
class Estimate:
    """A rough size of a run, shown before asking to confirm."""

    passages: int
    batches: int
    tokens: int
    seconds: int
    basis: str


def estimate(ws: Workspace, passages: int, batch_size: int) -> Estimate:
    """Estimate tokens and time: from this workspace's last successful run when there is one, else from C3."""
    batches = max(1, math.ceil(passages / max(1, batch_size)))
    for run_dir in sorted(ws.runs_dir.glob("*"), reverse=True):
        run, taxonomy = load(run_dir), find_taxonomy(run_dir)
        if not run or run.status != "ok" or taxonomy is None:
            continue
        metrics = json.loads(taxonomy.read_text(encoding="utf-8")).get("run_metrics") or {}
        if metrics.get("total_tokens") and run.passages:
            scale = passages / run.passages
            return Estimate(passages, batches, int(metrics["total_tokens"] * scale),
                            int(metrics.get("elapsed_seconds", 0) * scale), f"scaled from run {run_dir.name}")
    return Estimate(passages, batches, passages * TOKENS_PER_PASSAGE, passages * SECONDS_PER_PASSAGE,
                    "rough, from the C3 sample")


def read_corpus(path: Path) -> List[Dict]:
    """Return the passages of a corpus JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_corpus(path: Path, passages: List[Dict]) -> None:
    """Write passages as a corpus JSON file."""
    path.write_text(json.dumps(passages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
