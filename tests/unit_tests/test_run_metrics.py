"""Tests for run_metrics/mode persistence in main.py's run() (Plan U1)."""

import argparse
import asyncio
import json
from pathlib import Path

import main as main_module


class _EmptyGraph:
    """Stand-in for the compiled LangGraph graph: yields no pipeline events."""

    async def astream(self, invoke_input, config=None, stream_mode=None):
        return
        yield  # pragma: no cover - makes this an async generator


class _FakeTokenTracker:
    """Stand-in for TokenTracker with preset, nonzero token counts."""

    def __init__(self) -> None:
        self.total_tokens = 1234
        self.prompt_tokens = 1000
        self.completion_tokens = 234


def _make_args(tmp_path: Path, output: bool) -> argparse.Namespace:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("doc one\ndoc two\n")
    return argparse.Namespace(
        corpus=str(corpus),
        taxonomy=None,
        mode="train",
        feedback=None,
        feedback_file=None,
        config=None,
        model=None,
        fast_model=None,
        name="run-metrics-test",
        max_clusters=None,
        output=str(tmp_path / "out") if output else None,
        quiet=True,
        visualize=None,
        report=None,
        evaluate=None,
        iteration=None,
        axis_positions="auto",
        no_auto_report=True,
    )


def _saved_taxonomy_json(output_dir: Path) -> dict:
    matches = list(output_dir.glob("*_taxonomy_*.json"))
    assert len(matches) == 1, f"expected exactly one saved taxonomy JSON, found {matches}"
    with open(matches[0]) as f:
        return json.load(f)


def test_run_metrics_and_mode_persisted_with_output(tmp_path, monkeypatch):
    """A full pipeline run with --output writes run_metrics and mode."""
    monkeypatch.setattr(main_module, "graph", _EmptyGraph())
    monkeypatch.setattr(main_module, "TokenTracker", _FakeTokenTracker)

    args = _make_args(tmp_path, output=True)
    asyncio.run(main_module.run(args))

    data = _saved_taxonomy_json(Path(args.output))
    assert data["mode"] == "train"
    run_metrics = data["run_metrics"]
    assert isinstance(run_metrics["elapsed_seconds"], (int, float))
    assert run_metrics["elapsed_seconds"] >= 0
    assert run_metrics["total_tokens"] == 1234
    assert run_metrics["prompt_tokens"] == 1000
    assert run_metrics["completion_tokens"] == 234


def test_run_metrics_total_tokens_zero_is_written_not_omitted(tmp_path, monkeypatch):
    """When no LLM calls happen, total_tokens is 0, not omitted (per Assumptions)."""
    monkeypatch.setattr(main_module, "graph", _EmptyGraph())
    # Real TokenTracker, never invoked by the empty stream -> counts stay 0.

    args = _make_args(tmp_path, output=True)
    asyncio.run(main_module.run(args))

    data = _saved_taxonomy_json(Path(args.output))
    assert "run_metrics" in data
    assert data["run_metrics"]["total_tokens"] == 0
    assert data["run_metrics"]["prompt_tokens"] == 0
    assert data["run_metrics"]["completion_tokens"] == 0


def test_no_output_dir_means_no_files_written(tmp_path, monkeypatch):
    """Without --output, no taxonomy JSON (and so no run_metrics) is ever written."""
    monkeypatch.setattr(main_module, "graph", _EmptyGraph())

    args = _make_args(tmp_path, output=False)
    asyncio.run(main_module.run(args))

    assert not (tmp_path / "out").exists()
