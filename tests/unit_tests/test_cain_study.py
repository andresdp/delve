"""study/cain2027: inputs, workspaces, session runner and scoring for the CAIN 2027 agent study."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

from delvedspace.workspace import read_json
from tests.unit_tests.test_ddspace_import import _model
from tests.unit_tests.test_wiki_export import _taxonomy

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"cain_{name}", ROOT / "study" / "cain2027" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = _load("build_workspaces")

CONFIG = """models:
  generation_llm: openai/gpt-5.6-luna
  evaluation_llm: openai/gpt-5.6-luna
  embedding: openai/text-embedding-3-small
taxonomy:
  use_case: Design decisions for a toy system.
pipeline:
  batch_size: 20
"""


@pytest.fixture
def source_run(tmp_path):
    """A pipeline run folder with a full taxonomy (history included), its config, the sources and a model."""
    run = tmp_path / "run"
    run.mkdir()
    taxonomy = _taxonomy()
    taxonomy.update({"operation_log": [{"op": "add_value", "text": "x" * 500}], "evaluation_history": [{"x": 1}],
                     "saturation_history": [{"batch_index": 0}],
                     "iterations": [{"clusters": []}] + taxonomy["iterations"]})
    (run / "toy_taxonomy_20261016_000000.json").write_text(json.dumps(taxonomy))
    (run / "config.yaml").write_text(CONFIG)
    sources = tmp_path / "sources.csv"
    with sources.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "url"])
        w.writerows([["s1", "First", "https://example.org/1"], ["s2", "Second", "https://example.org/2"]])
    model = tmp_path / "gt_model.json"
    model.write_text(json.dumps(_model()))
    return run, sources, model


@pytest.fixture
def inputs(tmp_path, source_run):
    run, sources, model = source_run
    out = tmp_path / "inputs"
    build.prepare(run, model, sources, out)
    return out


# ---------------------------------------------------------------- U4: inputs and workspaces


def test_trimmed_taxonomy_keeps_the_design_space(inputs, source_run):
    run, _, _ = source_run
    full = json.loads(next(run.glob("*_taxonomy_*.json")).read_text())
    trimmed = read_json(next(inputs.glob("*_taxonomy_*.json")))
    assert trimmed["selected_clusters"] == full["selected_clusters"]
    assert trimmed["iterations"] == full["iterations"][-1:]
    assert "operation_log" not in trimmed and "evaluation_history" not in trimmed


def test_manifest_hashes_every_input(inputs):
    manifest = read_json(inputs / "manifest.json")
    assert set(manifest["files"]) == {p.name for p in inputs.iterdir() if p.name != "manifest.json"}
    assert build.verify(inputs) == []
    (inputs / "sources.csv").write_text("id,title,url\n")
    assert build.verify(inputs) == ["sources.csv"]


def test_config_with_an_absolute_path_is_refused(tmp_path, source_run):
    run, sources, model = source_run
    (run / "config.yaml").write_text(CONFIG + "output:\n  default_output_dir: /Users/someone/out\n")
    with pytest.raises(ValueError, match="absolute path"):
        build.prepare(run, model, sources, tmp_path / "inputs")


def test_build_makes_three_workspaces_from_tracked_inputs(inputs, tmp_path):
    out = tmp_path / "workspaces"
    build.build(inputs, out)
    assert sorted(p.name for p in out.iterdir()) == ["E", "M", "N"]
    assert list((out / "N").iterdir()) == []
    for cond in ("M", "E"):
        ws = out / cond
        assert (ws / "raw" / "graph.json").is_file() and (ws / "AGENTS.md").is_file()
        assert read_json(ws / build.MANIFEST_COPY) == read_json(inputs / "manifest.json")
        graph = read_json(ws / "raw" / "graph.json")
        assert not [n for n in graph["nodes"] if n["id"].startswith("p:")]        # no sampled design points
    assert "expert decision model" in (out / "E" / "AGENTS.md").read_text()
    assert "mined from practitioner sources" in (out / "M" / "AGENTS.md").read_text()


def test_build_twice_leaves_no_leftovers(inputs, tmp_path):
    out = tmp_path / "workspaces"
    build.build(inputs, out)
    (out / "M" / "stray.txt").write_text("old")
    build.build(inputs, out)
    assert not (out / "M" / "stray.txt").exists()
    assert len(list((out / "M" / "runs").iterdir())) == 1


def test_build_refuses_inputs_that_changed(inputs, tmp_path):
    (inputs / "config.yaml").write_text(CONFIG.replace("20", "8"))
    with pytest.raises(ValueError, match="config.yaml"):
        build.build(inputs, tmp_path / "workspaces")
