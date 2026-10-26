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
    (run / "config.yaml").write_text(CONFIG + "output:\n  default_output_dir: /srv/someone/out\n")
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
    "decisions": [{"decision": "Model serving", "context": "Scores are needed before authorization.",
                   "drivers": ["latency under 50 ms", "auditability"],
                   "rationale": "Low latency matters most.",
                   "alternatives": [{"label": "Model as a service", "value_id": "v:3.1", "citations": ["s03_p02"],
                                     "pros": ["scales independently"], "cons": ["network hop"]},
                                    {"label": "Embedded model", "value_id": "v:3.2", "citations": [],
                                     "pros": ["no network hop"], "cons": ["redeploy to update"]}],
                   "chosen": {"label": "Model as a service", "value_id": "v:3.1"},
                   "consequences": ["Needs a model registry."]}],
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
    argv = sessions.command(s, tmp_path / "ws", tmp_path / "last.json", model=SETTINGS["model"])
    assert argv[:2] == ["codex", "exec"] and "--json" in argv
    assert argv[argv.index("-m") + 1] == "gpt-5.6-luna"
    assert argv[argv.index("--output-schema") + 1] == str(design.SCHEMA)
    assert argv[argv.index("-C") + 1] == str(tmp_path / "ws")
    assert 'web_search="disabled"' in argv and "sandbox_workspace_write.network_access=true" in argv
    n = sessions.command(sessions.Session("fraud", "N", 1), tmp_path / "ws", tmp_path / "last.json", model=SETTINGS["model"])
    assert "sandbox_workspace_write.network_access=true" not in n


def test_preflight_refuses_web_search_a_shared_model_and_a_foreign_workspace(tmp_path, inputs):
    s = sessions.Session("fraud", "M", 1)
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / build.MANIFEST_COPY).write_text((inputs / "manifest.json").read_text())
    argv = sessions.command(s, ws, tmp_path / "last.json", model=SETTINGS["model"])
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
    summary = sessions.summarize(events, home="/srv/someone", secrets=[])
    assert summary["ddspace_calls"] == {"query dims": 1, "query values": 1, "point": 1}
    assert summary["points"] == [{"values": ["Model as a service", "Batch scoring"], "ok": True, "warnings": 1,
                                  "attested": 1, "llm": False}]
    assert summary["tokens"] == {"input": 1000, "cached_input": 400, "output": 50, "reasoning": 10}
    assert summary["complete"] is True and summary["network_commands"] == 0 and summary["web_search"] == 0


def test_summary_keeps_no_paths_usernames_or_keys():
    key = "sk-proj-abcdefghijklmnopqrstuvwxyz"
    events = _events(_cmd(f"ls /srv/someone/space && echo {key}", "someone wheel"),
                     _cmd('ddspace point "/srv/someone/x" "sk-proj-zzzzzzzzzzzzzzzzzzzz"'))
    text = json.dumps(sessions.summarize(events, home="/srv/someone", secrets=[key]))
    assert "/srv/someone" not in text and "someone" not in text and "sk-proj" not in text


def test_summary_flags_network_commands_and_web_search():
    events = _events(_cmd("curl https://example.org"), _cmd("pip install requests"),
                     {"type": "item.completed", "item": {"type": "web_search", "query": "mlops"}})
    summary = sessions.summarize(events, home="/srv/someone", secrets=[])
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


# ---------------------------------------------------------------- U6: scoring

score = _load("score")


def _gt():
    """Three decisions: storage (lake, warehouse), serving (service, embedded), labelling (manual, weak)."""
    return {"decisions": [{"id": "storage", "name": "Data storage"}, {"id": "serving", "name": "Model serving"},
                          {"id": "labels", "name": "Labelling"}],
            "options": [{"id": "lake", "name": "Data lake", "decision_ids": ["storage"]},
                        {"id": "warehouse", "name": "Data warehouse", "decision_ids": ["storage"]},
                        {"id": "service", "name": "Model as a service", "decision_ids": ["serving"]},
                        {"id": "embedded", "name": "Embedded model", "decision_ids": ["serving"]},
                        {"id": "manual", "name": "Manual labelling", "decision_ids": ["labels"]},
                        {"id": "weak", "name": "Weak supervision", "decision_ids": ["labels"]}],
            "forces": [{"id": "low_latency", "name": "Low latency"}, {"id": "reduce_cost", "name": "Reduce cost"},
                       {"id": "other", "name": "Other"}],
            "impacts": [{"option_id": "service", "force_id": "low_latency", "impact": "--"},
                        {"option_id": "embedded", "force_id": "low_latency", "impact": "++"},
                        {"option_id": "lake", "force_id": "reduce_cost", "impact": "+"},
                        {"option_id": "warehouse", "force_id": "reduce_cost", "impact": "-"},
                        {"option_id": "manual", "force_id": "other", "impact": "+"}]}


BRIEF = {"id": "fraud", "forces": ["low_latency", "reduce_cost"]}


def _design(*decisions):
    out = []
    for name, alts, chosen in decisions:
        out.append({"decision": name, "context": "c", "drivers": [], "rationale": "r", "consequences": [],
                    "chosen": {"label": chosen, "value_id": None},
                    "alternatives": [{"label": a, "value_id": None, "citations": [], "pros": [], "cons": []}
                                     for a in alts]})
    return {"decisions": out, "uncovered": []}


def _hits(design_doc, mapping):
    """Hits per item id from a label -> expert option ids mapping."""
    return {item.id: set(mapping.get(item.name, ())) for item in score.design_items(design_doc)}


def test_briefs_must_name_known_forces_with_impacts():
    score.check_briefs([BRIEF], _gt())
    with pytest.raises(ValueError, match="unknown"):
        score.check_briefs([{"id": "x", "forces": ["no_such_force"]}], _gt())
    gt = _gt()
    gt["impacts"] = []
    with pytest.raises(ValueError, match="no impact"):
        score.check_briefs([BRIEF], gt)


def test_decision_coverage_counts_expert_decisions_with_a_match():
    d = _design(("Serving", ["Online service", "On-device model"], "On-device model"),
                ("Storage", ["Lake", "Warehouse"], "Lake"))
    m = score.metrics(d, _hits(d, {"Online service": ["service"], "On-device model": ["embedded"], "Lake": ["lake"]}),
                      _gt(), BRIEF, "N")
    assert m["decision_coverage"] == pytest.approx(2 / 3) and m["expert_decisions_matched"] == 2
    assert m["alternatives_per_decision"] == 2 and m["alternatives_matched"] == pytest.approx(3 / 4)


def test_requirements_fit_is_one_for_the_best_and_zero_for_the_worst():
    d = _design(("Serving", ["Online service", "On-device model"], "On-device model"),
                ("Storage", ["Lake", "Warehouse"], "Warehouse"))
    hits = _hits(d, {"Online service": ["service"], "On-device model": ["embedded"], "Lake": ["lake"],
                     "Warehouse": ["warehouse"]})
    m = score.metrics(d, hits, _gt(), BRIEF, "N")
    assert m["fit_by_decision"] == {"serving": 1.0, "storage": 0.0}
    assert m["requirements_fit"] == 0.5 and m["choices_matched"] == 2 and m["choices_unmatched"] == 0


def test_fit_excludes_ties_and_records_unmatched_choices():
    d = _design(("Labels", ["Manual", "Weak"], "Manual"), ("Serving", ["Online service", "GPU box"], "GPU box"))
    m = score.metrics(d, _hits(d, {"Manual": ["manual"], "Weak": ["weak"], "Online service": ["service"]}),
                      _gt(), BRIEF, "N")
    assert m["fit_by_decision"] == {} and m["requirements_fit"] is None     # labels tie on the brief's forces
    assert m["choices_unmatched"] == 1 and m["fit_excluded_ties"] == 1


def test_fit_with_a_zero_best_and_negative_others_lies_between():
    gt = _gt()
    gt["impacts"] = [{"option_id": "service", "force_id": "low_latency", "impact": "-"},
                     {"option_id": "embedded", "force_id": "low_latency", "impact": "o"},
                     {"option_id": "embedded", "force_id": "reduce_cost", "impact": "--"},
                     {"option_id": "service", "force_id": "reduce_cost", "impact": "+"}]
    d = _design(("Serving", ["Online service", "On-device model"], "Online service"))
    m = score.metrics(d, _hits(d, {"Online service": ["service"], "On-device model": ["embedded"]}), gt, BRIEF, "N")
    assert 0.0 < m["fit_by_decision"]["serving"] <= 1.0


def test_grounding_and_consistency_need_a_space():
    d = _design(("Serving", ["Online service", "On-device model"], "On-device model"))
    m = score.metrics(d, _hits(d, {}), _gt(), BRIEF, "N")
    assert m["grounded_choices"] is None and m["consistency_warnings"] is None and m["points_explored"] is None


def test_citations_to_ids_outside_the_graph_are_ungrounded():
    graph = {"nodes": [{"id": "d:1", "kind": "dimension"}, {"id": "v:1.1", "kind": "value", "dimension_id": "d:1",
                        "passages": [{"doc": "s01_p02", "stance": "accepted"}]}], "edges": []}
    d = _design(("Serving", ["Online service", "On-device model"], "Online service"))
    d["decisions"][0]["alternatives"][0]["citations"] = ["s01_p02", "s09_p99"]
    m = score.metrics(d, _hits(d, {}), _gt(), BRIEF, "M", graph=graph)
    assert m["grounded_choices"] == 1.0 and m["valid_citations"] == 0.5


def test_cost_comes_from_the_dated_rate_table():
    summary = {"model": "m1", "tokens": {"input": 2_000_000, "cached_input": 1_000_000, "output": 100_000,
                                         "reasoning": 0}, "points": [], "network_commands": 0}
    rates = {"date": "2026-10-25", "models": {"m1": {"input": 1.0, "cached_input": 0.1, "output": 10.0}}}
    d = _design(("Serving", ["A", "B"], "A"))
    m = score.metrics(d, _hits(d, {}), _gt(), BRIEF, "N", summary=summary, rates=rates)
    assert m["cost_usd"] == pytest.approx(1.0 + 0.1 + 1.0)
    assert score.metrics(d, _hits(d, {}), _gt(), BRIEF, "N", summary=summary, rates={"models": {}})["cost_usd"] is None


def test_summary_without_point_events_is_rejected():
    with pytest.raises(ValueError, match="point events"):
        score.check_summary({"tokens": {}, "complete": True})


def test_matching_reuses_the_matcher_and_its_cache(tmp_path):
    import numpy as np

    from taxonomy_generator.evaluation import gt_match

    d = _design(("Serving", ["Online service", "On-device model"], "On-device model"))
    table = {"Online service": [1, 0, 0], "On-device model": [0, 1, 0], "Model as a service": [1, 0.01, 0],
             "Embedded model": [0.01, 1, 0], "Data lake": [0, 0, 1], "Data warehouse": [0, 0.1, 1],
             "Manual labelling": [0.5, 0, 0.5], "Weak supervision": [0.5, 0.5, 0]}

    def embed(texts):
        return np.asarray([next(v for k, v in table.items() if k in t) for t in texts], dtype=float)

    config = gt_match.MatcherConfig(matching_llm=None, generation_llm=None, embedding="x", lower_threshold=0.0,
                                    upper_threshold=0.6, max_candidates=5, include_outcomes=False,
                                    min_alignment_share=0.25, seed=0, cache_path=str(tmp_path / "cache.json"),
                                    mode="embeddings")
    hits = score.match(d, _gt(), config, embed=embed)
    by_name = {i.name: hits[i.id] for i in score.design_items(d)}
    assert by_name["Online service"] == {"service"} and by_name["On-device model"] == {"embedded"}


def test_fit_classifies_each_expert_decision_once():
    d = _design(("Serving", ["GPU box", "Online service"], "GPU box"),
                ("Hosting", ["On-device model", "Edge cache"], "On-device model"))
    hits = _hits(d, {"Online service": ["service"], "On-device model": ["embedded"]})
    m = score.metrics(d, hits, _gt(), BRIEF, "N")
    assert m["choices_unmatched"] + m["choices_matched"] == 1      # "serving" counted once, not twice


def test_consistency_flags_two_values_of_one_dimension_and_unknown_ids():
    graph = {"nodes": [{"id": "d:1", "kind": "dimension", "label": "Serving"},
                       {"id": "v:1.1", "kind": "value", "label": "Service", "dimension_id": "d:1", "dimension": "Serving",
                        "status": "accepted"},
                       {"id": "v:1.2", "kind": "value", "label": "Embedded", "dimension_id": "d:1",
                        "dimension": "Serving", "status": "accepted"}], "edges": []}
    d = _design(("Serving", ["Service", "Embedded"], "Service"), ("Serving again", ["Embedded", "X"], "Embedded"),
                ("Other", ["Y", "Z"], "Y"))
    d["decisions"][0]["chosen"]["value_id"] = "v:1.1"
    d["decisions"][1]["chosen"]["value_id"] = "v:1.2"
    d["decisions"][2]["chosen"]["value_id"] = "v:9.9"
    m = score.metrics(d, _hits(d, {}), _gt(), BRIEF, "E", graph=graph)
    assert m["consistency_warnings"] >= 1 and m["unknown_value_ids"] == 1 and m["value_ids_used"] == 3


def test_environment_is_an_allow_list_and_keys_follow_the_condition(tmp_path, monkeypatch):
    bin_dir = tmp_path / "envbin"
    bin_dir.mkdir()
    (bin_dir / "ddspace").write_text("")
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_secret")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-operator-key-000000000")
    n = sessions._environment(sessions.Session("b", "N", 1), tmp_path / "home", bin_dir / "ddspace", "sk-study")
    assert str(bin_dir) not in n["PATH"] and "OPENAI_API_KEY" not in n and "GITHUB_TOKEN" not in n
    m = sessions._environment(sessions.Session("b", "M", 1), tmp_path / "home", bin_dir / "ddspace", "sk-study")
    assert m["PATH"].split(":")[0] == str(bin_dir) and m["OPENAI_API_KEY"] == "sk-study"
    assert "GITHUB_TOKEN" not in m and m["CODEX_HOME"] == str(tmp_path / "home")


def test_network_use_chained_with_ddspace_is_still_counted():
    events = _events(_cmd("ddspace query dims && curl https://example.org"))
    assert sessions.summarize(events, home="/x", secrets=[])["network_commands"] == 1
    assert sessions.summarize(_events(_cmd("ddspace query dims")), home="/x", secrets=[])["network_commands"] == 0


def test_inside_refuses_the_folder_itself(tmp_path):
    assert sessions.inside(tmp_path, tmp_path) and sessions.inside(tmp_path / "a", tmp_path)
    assert not sessions.inside(tmp_path.parent / "elsewhere", tmp_path)


class _Proc:
    def __init__(self, stdout, code=0):
        self.stdout, self.stderr, self.returncode = stdout, "", code


def _fake_codex(monkeypatch, stdout, design_doc=None, raise_timeout=False):
    def fake_run(argv, **kwargs):
        if design_doc is not None:
            Path(argv[argv.index("-o") + 1]).write_text(json.dumps(design_doc))
        if raise_timeout:
            raise sessions.subprocess.TimeoutExpired(argv, kwargs.get("timeout"), output=stdout)
        return _Proc(stdout)
    monkeypatch.setattr(sessions.subprocess, "run", fake_run)


def _jsonl(*events):
    return "\n".join(json.dumps(e) for e in events) + "\n"


def test_run_writes_a_redacted_design_and_summary(tmp_path, monkeypatch):
    stdout = _jsonl(*_events(_cmd("ls"))) + "not json\n"
    doc = json.loads(json.dumps(FIXTURE_DESIGN))
    doc["decisions"][0]["rationale"] = f"see {Path.home()}/notes"
    _fake_codex(monkeypatch, stdout, doc)
    rec = sessions.run(sessions.Session("fraud", "N", 1), {"system": "S", "text": "T"}, tmp_path / "ws",
                       tmp_path / "scratch", model="m-test", results=tmp_path / "results")
    assert rec["status"] == "ok" and rec["exit_code"] == 0
    saved = (tmp_path / "results" / "designs" / "fraud-N-r1.json").read_text()
    assert str(Path.home()) not in saved and not (tmp_path / "scratch" / "fraud-N-r1").exists()


def test_timed_out_session_fails_and_leaves_no_login(tmp_path, monkeypatch):
    _fake_codex(monkeypatch, _jsonl({"type": "turn.started"}), FIXTURE_DESIGN, raise_timeout=True)
    rec = sessions.run(sessions.Session("fraud", "N", 1), {"system": "S", "text": "T"}, tmp_path / "ws",
                       tmp_path / "scratch", model="m-test", results=tmp_path / "results", keep_raw=True,
                       timeout=5)
    assert rec["status"] == "failed" and "timed out after 5 s" in rec["problems"]
    assert not (tmp_path / "results" / "designs" / "fraud-N-r1.json").exists()
    assert not (tmp_path / "scratch" / "fraud-N-r1" / "codex-home").exists()


def test_adrs_render_as_concise_madr_markdown():
    files = design.render_adrs(FIXTURE_DESIGN, "Card-fraud scoring service")
    assert list(files) == ["0001-model-serving.md"]
    text = files["0001-model-serving.md"]
    for heading in ("# Model serving", "## Context and Problem Statement", "## Decision Drivers",
                    "## Considered Options", "## Decision Outcome", "### Consequences"):
        assert heading in text
    assert "Chosen option: \"Model as a service\" (`v:3.1`)" in text and "Good, because scales independently" in text
    assert "Bad, because redeploy to update" in text and "s03_p02" in text


def test_run_writes_the_adrs_of_a_valid_design(tmp_path, monkeypatch):
    _fake_codex(monkeypatch, _jsonl(*_events()), FIXTURE_DESIGN)
    sessions.run(sessions.Session("fraud", "N", 1), {"system": "Fraud", "text": "T"}, tmp_path / "ws",
                 tmp_path / "scratch", model="m-test", results=tmp_path / "results")
    assert (tmp_path / "results" / "adrs" / "fraud-N-r1" / "0001-model-serving.md").is_file()


def test_driver_recall_counts_the_brief_forces_the_drivers_name():
    d = _design(("Serving", ["A", "B"], "A"))
    m = score.metrics(d, _hits(d, {}), _gt(), BRIEF, "N", driver_hits={"low_latency"})
    assert m["driver_recall"] == 0.5 and m["drivers_listed"] == 0
    assert score.metrics(d, _hits(d, {}), _gt(), BRIEF, "N")["driver_recall"] is None


def test_drivers_are_matched_to_force_names(tmp_path):
    import numpy as np

    from taxonomy_generator.evaluation import gt_match

    d = _design(("Serving", ["A", "B"], "A"))
    d["decisions"][0]["drivers"] = ["fast responses", "cheap to run"]
    table = {"fast responses": [1, 0, 0], "cheap to run": [0, 1, 0], "Low latency": [1, 0.01, 0],
             "Reduce cost": [0.01, 1, 0], "Other": [0, 0, 1]}

    def embed(texts):
        return np.asarray([next(v for k, v in table.items() if k in t) for t in texts], dtype=float)

    config = gt_match.MatcherConfig(matching_llm=None, generation_llm=None, embedding="x", lower_threshold=0.0,
                                    upper_threshold=0.6, max_candidates=5, include_outcomes=False,
                                    min_alignment_share=0.25, seed=0, cache_path=None, mode="embeddings")
    assert score.match_drivers(d, _gt(), BRIEF, config, embed=embed) == {"low_latency", "reduce_cost"}


def test_native_prefix_only_applies_on_macos(monkeypatch):
    monkeypatch.setattr(sessions.sys, "platform", "linux")
    assert sessions.native_prefix() == []


# ---------------------------------------------------------------- layer 1: the expert reference

reference = _load("reference")


def test_relevant_decisions_are_those_whose_options_differ_on_the_brief_forces():
    ref = score.relevant_decisions(_gt(), BRIEF["forces"])
    assert set(ref) == {"serving", "storage"}                       # labels only moves "other"
    assert ref["serving"]["preferred"] == ["embedded"] and ref["storage"]["sums"] == {"lake": 1, "warehouse": -1}


def test_relevant_decision_coverage_counts_only_relevant_decisions():
    d = _design(("Labels", ["Manual", "Weak"], "Manual"), ("Storage", ["Lake", "Warehouse"], "Lake"))
    m = score.metrics(d, _hits(d, {"Manual": ["manual"], "Lake": ["lake"]}), _gt(), BRIEF, "N")
    assert m["decision_coverage"] == pytest.approx(2 / 3)
    assert m["relevant_decision_coverage"] == 0.5 and m["relevant_decisions_matched"] == 1


def test_reference_ranks_options_and_marks_the_preferred():
    ref = reference.reference(_gt(), {**BRIEF, "system": "Fraud"})
    serving = next(d for d in ref["relevant_decisions"] if d["id"] == "serving")
    assert [o["id"] for o in serving["options"]] == ["embedded", "service"]
    assert serving["options"][0]["preferred"] and serving["options"][0]["impacts"] == ["Low latency ++"]
    text = reference.render(ref, draft=True)
    assert "DRAFT" in text and "| **Embedded model** | +2 |" in text and "Relevant decisions: 2 of 3" in text


# ---------------------------------------------------------------- layer 3: the blind rating kit

rating = _load("rating")


def test_quadratic_kappa_matches_sklearn():
    sklearn_metrics = pytest.importorskip("sklearn.metrics")
    a, b = [1, 2, 3, 4, 4, 2, 3, 1], [1, 3, 3, 4, 3, 2, 4, 2]
    assert rating.qwk(a, b) == pytest.approx(sklearn_metrics.cohen_kappa_score(a, b, weights="quadratic"))
    assert rating.qwk(a, a) == 1.0 and rating.qwk([3, 3], [3, 3]) is None


def test_packet_hides_ids_citations_and_the_system_line():
    doc = json.loads(json.dumps(FIXTURE_DESIGN))
    doc["decisions"][0]["alternatives"][0].update(value_id="v:9.6", citations=["s04_p02"])
    doc["decisions"][0]["chosen"]["value_id"] = "v:9.6"
    doc["decisions"][0]["rationale"] = "As `v:9.6` and s04_p02 say, d:1 matters; v:9.60 is not an id here."
    text = rating.packet(doc, {"system": "Fraud", "text": "Score cards."}, "P123", ["v:9.6", "s04_p02", "d:1"])
    assert "v:9.6`" not in text and "s04_p02" not in text and " d:1 " not in text and "v:9.60" in text
    assert "Sources:" not in text and "System: Fraud" not in text and "Score cards." in text


def test_kit_writes_packets_sheets_and_a_separate_key(tmp_path):
    briefs = [{"id": "fraud", "system": "Fraud", "text": "T"}]
    (tmp_path / "designs").mkdir()
    for cond in "NME":
        (tmp_path / "designs" / f"fraud-{cond}-r1.json").write_text(json.dumps(FIXTURE_DESIGN))
    key = rating.build_kit(1, ["A", "B"], 7, None, results=tmp_path, briefs=briefs)
    assert sorted(key.values()) == ["fraud-E-r1", "fraud-M-r1", "fraud-N-r1"]
    kit = tmp_path / "rating"
    assert sorted(p.stem for p in (kit / "packets").glob("*.md")) == sorted(key)
    assert not any("fraud-" in p.read_text() for p in kit.rglob("*.*"))         # the key lives elsewhere
    with (kit / "sheet-A.csv").open() as f:
        assert sorted(r["packet"] for r in csv.DictReader(f)) == sorted(key)
    with pytest.raises(SystemExit, match="already exists"):
        rating.build_kit(1, ["A", "B"], 7, None, results=tmp_path, briefs=briefs)


def test_agreement_lists_disagreements_of_two_points_and_unblinds_per_condition():
    a = {"P1": dict(coverage=4, tradeoffs=3, fit=3, correctness=4), "P2": dict(coverage=2, tradeoffs=2, fit=1, correctness=3)}
    b = {"P1": dict(coverage=4, tradeoffs=3, fit=1, correctness=4), "P2": dict(coverage=2, tradeoffs=3, fit=1, correctness=3)}
    out = rating.agreement(a, b)
    assert out["to_resolve"] == [{"packet": "P1", "item": "fit", "scores": [3, 1]}]
    assert out["kappa"]["coverage"] == 1.0
    means = rating.by_condition(a, {"P1": "fraud-N-r1", "P2": "fraud-M-r1"})
    assert means["N"]["coverage"] == 4 and means["M"]["fit"] == 1


def test_incomplete_sheets_are_refused(tmp_path):
    sheet = tmp_path / "sheet-A.csv"
    sheet.write_text("packet,coverage,tradeoffs,fit,correctness,notes\nP1,4,3,,2,\n")
    with pytest.raises(SystemExit, match="no valid fit"):
        rating.read_sheet(sheet)


# ---------------------------------------------------------------- strict matching readings


def _pair(item, gt_id, label, distance):
    return {"system_id": item, "gt_id": gt_id, "label": label, "distance": distance}


def test_hit_levels_keep_one_best_match_per_alternative():
    pairs = [_pair("d0a0", "lake", "broader", 0.2), _pair("d0a0", "warehouse", "same", 0.3),
             _pair("d0a1", "service", "narrower", 0.4), _pair("d0a1", "embedded", "broader", 0.25)]
    levels = score.hit_levels(["d0a0", "d0a1", "d0a2"], pairs)
    assert levels["best"] == {"d0a0": {"warehouse"}, "d0a1": {"embedded"}, "d0a2": set()}   # "same" wins
    assert levels["same"] == {"d0a0": {"warehouse"}, "d0a1": set(), "d0a2": set()}
    assert levels["lenient"]["d0a0"] == {"lake", "warehouse"}


def test_one_broad_alternative_no_longer_covers_many_decisions():
    d = _design(("Platform", ["Everything platform", "Nothing"], "Everything platform"))
    item = score.design_items(d)[0].id
    pairs = [_pair(item, "lake", "broader", 0.3), _pair(item, "service", "broader", 0.35),
             _pair(item, "manual", "broader", 0.4)]
    levels = score.hit_levels([i.id for i in score.design_items(d)], pairs)
    m = score.metrics(d, levels["best"], _gt(), BRIEF, "N", same_hits=levels["same"], lenient_hits=levels["lenient"])
    assert m["expert_decisions_matched"] == 1 and m["expert_decisions_matched_lenient"] == 3
    assert m["expert_decisions_matched_same"] == 0 and m["decision_coverage_same"] == 0
    assert m["relevant_decisions_matched"] == 1 and m["relevant_decisions_matched_lenient"] == 2
