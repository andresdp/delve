"""study/cain2027: inputs, workspaces, session runner and scoring for the CAIN 2027 agent study."""

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from delvedspace.workspace import read_json
from tests.unit_tests.test_ddspace_import import _model
from tests.unit_tests.test_wiki_export import _taxonomy

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"cain_{name}", ROOT / "study" / "cain2027" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # dataclasses look their module up while the class is built
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


# ---------------------------------------------------------------- U5: sessions

design = _load("design")
sessions = _load("run_sessions")

FIXTURE_DESIGN = {
    "decisions": [{"decision": "Model serving", "rationale": "Low latency matters most.",
                   "alternatives": [{"label": "Model as a service", "value_id": "v:3.1", "citations": ["s03_p02"]},
                                    {"label": "Embedded model", "value_id": "v:3.2", "citations": []}],
                   "chosen": {"label": "Model as a service", "value_id": "v:3.1"}}],
    "uncovered": ["Data labelling"],
}


def _cmd(text, out="", code=0):
    return {"type": "item.completed", "item": {"type": "command_execution", "command": f"/bin/zsh -lc '{text}'",
                                               "aggregated_output": out, "exit_code": code, "status": "completed"}}


def _events(*items, complete=True):
    events = [{"type": "thread.started", "thread_id": "t1"}, {"type": "turn.started"}, *items]
    if complete:
        events.append({"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 400,
                                                           "output_tokens": 50, "reasoning_output_tokens": 10}})
    return events


SETTINGS = dict(model="gpt-5.6-luna", matching_model="openai/gpt-5.4-mini")


def test_fixture_design_validates_against_the_schema():
    assert design.validate(FIXTURE_DESIGN) == []
    broken = json.loads(json.dumps(FIXTURE_DESIGN))
    del broken["decisions"][0]["chosen"]
    assert design.validate(broken)


def test_command_pins_model_schema_workspace_and_network_per_condition(tmp_path):
    s = sessions.Session("fraud", "M", 1)
    argv = sessions.command(s, tmp_path / "ws", tmp_path / "last.json", **SETTINGS)
    assert argv[:2] == ["codex", "exec"] and "--json" in argv
    assert argv[argv.index("-m") + 1] == "gpt-5.6-luna"
    assert argv[argv.index("--output-schema") + 1] == str(design.SCHEMA)
    assert argv[argv.index("-C") + 1] == str(tmp_path / "ws")
    assert 'web_search="disabled"' in argv and "sandbox_workspace_write.network_access=true" in argv
    n = sessions.command(sessions.Session("fraud", "N", 1), tmp_path / "ws", tmp_path / "last.json", **SETTINGS)
    assert "sandbox_workspace_write.network_access=true" not in n


def test_preflight_refuses_web_search_a_shared_model_and_a_foreign_workspace(tmp_path, inputs):
    s = sessions.Session("fraud", "M", 1)
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / build.MANIFEST_COPY).write_text((inputs / "manifest.json").read_text())
    argv = sessions.command(s, ws, tmp_path / "last.json", **SETTINGS)
    assert sessions.preflight(s, argv, ws, inputs / "manifest.json", **SETTINGS) == []
    web = [a for a in argv if a != 'web_search="disabled"']
    assert any("web search" in p for p in sessions.preflight(s, web, ws, inputs / "manifest.json", **SETTINGS))
    same = dict(SETTINGS, matching_model="openai/gpt-5.6-luna")
    assert any("matching" in p for p in sessions.preflight(s, argv, ws, inputs / "manifest.json", **same))
    (ws / build.MANIFEST_COPY).write_text("{}")
    assert any("manifest" in p for p in sessions.preflight(s, argv, ws, inputs / "manifest.json", **SETTINGS))


def test_summary_counts_ddspace_calls_points_and_tokens():
    point_out = json.dumps({"values": [{"id": "v:3.1"}, {"id": "v:4.2"}], "warnings": ["two values of one decision"],
                            "attested_by": [{"id": "s:s1"}]})
    events = _events(_cmd("ddspace query dims"), _cmd('ddspace query values "Model serving"'),
                     _cmd('/opt/env/bin/ddspace point "Model as a service" "Batch scoring" --no-llm', point_out))
    summary = sessions.summarize(events, home="/Users/someone", secrets=[])
    assert summary["ddspace_calls"] == {"query dims": 1, "query values": 1, "point": 1}
    assert summary["points"] == [{"values": ["Model as a service", "Batch scoring"], "ok": True, "warnings": 1,
                                  "attested": 1, "llm": False}]
    assert summary["tokens"] == {"input": 1000, "cached_input": 400, "output": 50, "reasoning": 10}
    assert summary["complete"] is True and summary["network_commands"] == 0 and summary["web_search"] == 0


def test_summary_keeps_no_paths_usernames_or_keys():
    key = "sk-proj-abcdefghijklmnopqrstuvwxyz"
    events = _events(_cmd(f"ls /Users/someone/space && echo {key}", "someone wheel"),
                     _cmd('ddspace point "/Users/someone/x" "sk-proj-zzzzzzzzzzzzzzzzzzzz"'))
    text = json.dumps(sessions.summarize(events, home="/Users/someone", secrets=[key]))
    assert "/Users/someone" not in text and "someone" not in text and "sk-proj" not in text


def test_summary_flags_network_commands_and_web_search():
    events = _events(_cmd("curl https://example.org"), _cmd("pip install requests"),
                     {"type": "item.completed", "item": {"type": "web_search", "query": "mlops"}})
    summary = sessions.summarize(events, home="/Users/someone", secrets=[])
    assert summary["network_commands"] == 2 and summary["web_search"] == 1


def test_incomplete_log_is_reported():
    summary = sessions.summarize(_events(_cmd("ls"), complete=False), home="/x", secrets=[])
    assert summary["complete"] is False


def test_postflight_fails_without_a_design_or_a_complete_log(tmp_path):
    last = tmp_path / "last.json"
    ok = sessions.summarize(_events(), home="/x", secrets=[])
    assert "no design" in sessions.postflight(ok, last)[0]
    last.write_text(json.dumps(FIXTURE_DESIGN))
    assert sessions.postflight(ok, last) == []
    incomplete = sessions.summarize(_events(complete=False), home="/x", secrets=[])
    assert any("complete" in p for p in sessions.postflight(incomplete, last))
    web = sessions.summarize(_events({"type": "item.completed", "item": {"type": "web_search"}}), home="/x", secrets=[])
    assert any("web search" in p for p in sessions.postflight(web, last))


def test_planned_sessions_skip_those_with_a_design(tmp_path):
    briefs = [{"id": "fraud"}, {"id": "vision"}]
    planned = sessions.plan(briefs, ["N", "M", "E"], 2)
    assert len(planned) == 12 and planned[0].id == "fraud-N-r1"
    (tmp_path / "designs").mkdir()
    (tmp_path / "designs" / "fraud-N-r1.json").write_text("{}")
    assert len(sessions.pending(planned, tmp_path)) == 11
