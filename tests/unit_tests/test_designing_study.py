"""study/designing2027: the session runner for the rationale search and explain study (E and N)."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from delvedspace import agent

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"designing_{name}", ROOT / "study" / "designing2027" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # dataclasses look their module up while the class is built
    spec.loader.exec_module(module)
    return module


runner = _load("run_sessions")
controls = runner.controls
REAL_RUN = subprocess.run


def _cmd(text, out="", code=0):
    return {"type": "item.completed", "item": {"type": "command_execution", "command": f"/bin/zsh -lc '{text}'",
                                               "aggregated_output": out, "exit_code": code, "status": "completed"}}


def _events(*items, complete=True):
    events = [{"type": "thread.started", "thread_id": "t1"}, {"type": "turn.started"}, *items]
    if complete:
        events.append({"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 400,
                                                           "output_tokens": 50, "reasoning_output_tokens": 10}})
    return events


def _jsonl(*events):
    return "\n".join(json.dumps(e) for e in events) + "\n"


def _case(folder, case_id, mode):
    d = folder / case_id
    d.mkdir(parents=True)
    (d / "case.yaml").write_text(f"id: {case_id}\nmode: {mode}\n")
    (d / "problem.md").write_text(f"# {case_id}\n\nA problem with requirements.\n")
    if mode == "explain":
        (d / "solution.md").write_text("The nodes keep data on local disks and commit with a quorum.\n")
    return d


@pytest.fixture
def cases(tmp_path):
    folder = tmp_path / "cases"
    for case_id, mode in (("kv-store", "search"), ("feed", "search"), ("kv-explain", "explain"),
                          ("feed-explain", "explain")):
        _case(folder, case_id, mode)
    return runner.load_cases(folder)


def _no_space(case_id="kv-store"):
    """A clean zero-shot search file (space: null, the agent's own names), as an N session writes it."""
    choice = {"dimension_id": "Storage", "value_id": "Storage: Local disks", "drivers": ["Q1"], "reason": "Survives a node failure."}
    other = {"dimension_id": "Storage", "value_id": "Storage: Log in S3", "drivers": ["Q1"], "reason": "S3 is already there."}
    step = lambda n, approach, c: {"step": n, "round": 1, "approach": approach, "move": "seed",  # noqa: E731
                                   "values": [c["value_id"]], "hypothesis": "h", "assessment": {"Q1": "meets"}, "tradeoffs": [],
                                   "observation": "o", "rating": "strong", "point": f"P{n}"}
    return {"schema": "ddspace-rationale/6", "id": case_id, "mode": "search",
            "space": None,
            "problem": {"title": "A store", "requirements": [{"id": "Q1", "text": "No committed write is lost."}]},
            "budget": {"max_points": 2},
            "points": [{"id": "P1", "values": ["Storage: Local disks"], "description": "Local disks.", "attested_by": []},
                       {"id": "P2", "values": ["Storage: Log in S3"], "description": "A log in S3.", "attested_by": []}],
            "approaches": [{"id": "A", "idea": "what if disks?", "status": "live"},
                           {"id": "B", "idea": "what if S3?", "status": "live"}],
            "trajectory": [step(1, "A", choice), step(2, "B", other)],
            "alternatives": [{"id": "A1", "name": "Disks", "approach": "A", "step": 1, "choices": [choice]},
                             {"id": "A2", "name": "S3", "approach": "B", "step": 2, "choices": [other]}],
            "adrs": [{"id": "ADR1", "title": "Storage", "drivers": ["Q1"], "context": "c", "options": [
                {"id": "O1", "name": "Disks", "values": ["Storage: Local disks"], "status": "chosen", "in": ["A1"], "pros": [],
                 "cons": [], "reason": "r"},
                {"id": "O2", "name": "S3", "values": ["Storage: Log in S3"], "status": "chosen", "in": ["A2"], "pros": [],
                 "cons": [], "reason": "r"}]}],
            "uncovered": [], "unaddressed": []}


def _with_space(uncovered=()):
    """An explain file with ids, a passage, a source and uncovered items (not checked against a graph here)."""
    return {"schema": "ddspace-rationale/6", "id": "kv-explain", "mode": "explain",
            "space": {"workspace": "c1", "run": "r", "graph_sha256": "abc"},
            "problem": {"title": "A store", "requirements": [{"id": "Q1", "text": "No write is lost."}]},
            "alternatives": [{"id": "S", "name": "The solution", "choices": [
                {"dimension_id": "d:1", "value_id": "v:1.1", "drivers": ["Q1"], "reason": "r",
                 "evidence": [{"doc": "s01_p01", "stance": "accepts"}], "solution_quote": "local disks",
                 "forced": True},
                {"dimension_id": "d:2", "value_id": "v:2.10", "drivers": ["Q1"], "reason": "r",
                 "solution_quote": "a quorum", "forced": None}], "step": 1}],
            "budget": {"max_points": 8},
            "trajectory": [{"step": 1, "move": "solution", "values": ["v:1.1", "v:2.10"], "hypothesis": "h",
                            "assessment": {"Q1": "meets"}, "tradeoffs": [], "observation": "o", "verdict": "grounded",
                            "point": "P1"}],
            "points": [{"id": "P1", "values": ["v:1.1", "v:2.10"], "description": None, "attested_by": ["s:s1"]}],
            "regions": [{"id": "G1", "name": "g", "values": ["v:1.1"], "step": 1, "drivers": ["Q1"], "reason": "r"}],
            "adrs": [{"id": "ADR1", "title": "Storage", "drivers": ["Q1"], "context": "c", "options": [
                {"id": "O1", "name": "Disks and quorum", "values": ["v:1.1", "v:2.10"], "status": "chosen", "in": ["S"],
                 "pros": [], "cons": [], "reason": "r"}]}],
            "uncovered": list(uncovered), "unaddressed": []}


# ---------------------------------------------------------------- plan, resume and cases


def test_plan_is_case_by_condition_by_repetition_and_resume_skips_finished(cases, tmp_path):
    planned = runner.plan(cases, ["E", "N"], 2)
    assert len(planned) == 16 and len({s.id for s in planned}) == 16
    assert planned[0].id == "feed-E-r1" and planned[0].case == "feed"   # cases in folder order
    results = tmp_path / "results"
    (results / "rationale").mkdir(parents=True)
    (results / "rationale" / "kv-store-E-r1.json").write_text("{}")
    (results / "summaries").mkdir()
    (results / "summaries" / "kv-store-E-r1.json").write_text(json.dumps({"status": "ok"}))
    (results / "summaries" / "kv-store-N-r1.json").write_text("{}")   # a summary alone: the session failed
    left = runner.pending(planned, results)
    assert len(left) == 15 and "kv-store-E-r1" not in {s.id for s in left}


def test_a_kept_file_counts_as_done_only_with_an_ok_summary(tmp_path):
    results = tmp_path / "results"
    (results / "rationale").mkdir(parents=True)
    (results / "summaries").mkdir()
    failed, ok, broken, none = (runner.Session("kv-store", "E", r) for r in (1, 2, 3, 4))
    for s in (failed, ok, broken, none):
        (results / "rationale" / f"{s.id}.json").write_text("{}")
    (results / "summaries" / f"{failed.id}.json").write_text(json.dumps({"status": "failed", "problems": ["x"]}))
    (results / "summaries" / f"{ok.id}.json").write_text(json.dumps({"status": "ok"}))
    (results / "summaries" / f"{broken.id}.json").write_text('{"status": "ok", "model"')   # truncated
    assert runner.pending([failed, ok, broken, none], results) == [failed, broken, none]


def test_guards_tolerate_an_unreadable_summary(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("## search\nnew\n")
    results = tmp_path / "results"
    (results / "summaries").mkdir(parents=True)
    (results / "summaries" / "a-N-r1.json").write_text('{"model": "gpt-te')
    (results / "summaries" / "a-E-r1.json").write_bytes(b"\xff\xfe")
    (results / "summaries" / "a-E-r1.json").write_text("[1, 2]")
    assert runner.guards(results, model="gpt-test", prompt=prompt, skills_via="files") == []


def test_cases_need_a_mode_and_explain_cases_a_solution(tmp_path):
    folder = tmp_path / "cases"
    _case(folder, "a", "search")
    loaded = runner.load_cases(folder)
    assert [(c["id"], c["mode"]) for c in loaded] == [("a", "search")]
    bad = _case(folder, "b", "explain")
    (bad / "solution.md").unlink()
    with pytest.raises(ValueError, match="solution.md"):
        runner.load_cases(folder)
    (bad / "solution.md").write_text("x")
    (bad / "case.yaml").write_text("id: b\nmode: extend\n")
    with pytest.raises(ValueError, match="mode"):
        runner.load_cases(folder)


# ---------------------------------------------------------------- summary


def test_summary_counts_rationale_check_and_build_as_two_word_commands():
    events = _events(_cmd("ddspace query dimensions"), _cmd("ddspace rationale check rationale/kv-store.json", "{}", 1),
                     _cmd("/opt/env/bin/ddspace rationale check rationale/kv-store.json", "{}"),
                     _cmd("ddspace rationale build rationale/kv-store.json"),
                     _cmd('ddspace point "v:1.1" --no-llm', json.dumps({"warnings": [], "attested_by": []})))
    summary = runner.summarize(events, home="/srv/someone", secrets=[])
    assert summary["ddspace_calls"] == {"query dimensions": 1, "rationale check": 2, "rationale build": 1, "point": 1}
    assert summary["check_runs"] == 2 and summary["complete"] is True
    assert summary["points"][0]["llm"] is False


# ---------------------------------------------------------------- fabrication audit


def test_fabrication_audit_flags_ids_no_command_returned():
    values = json.dumps({"dimension": {"id": "d:1"}, "values": [{"id": "v:1.1"}, {"id": "v:2.1"}]})
    evidence = json.dumps({"value": "v:1.1", "passages": [{"doc": "s01_p01"}]})
    events = _events(_cmd('ddspace query values "d:1"', values), _cmd('ddspace query evidence "v:1.1"', evidence),
                     _cmd("ddspace query dimensions", json.dumps([{"id": "d:1"}, {"id": "d:2"}])))
    audit = runner.fabrication_audit(_with_space(), events)
    assert audit["ids"] == 6
    # v:2.10 was never printed (v:2.1 is not v:2.10), nor was the source s:s1
    assert audit["missing"] == ["v:2.10", "s:s1"] and audit["candidate_only"] == []


def test_fabrication_audit_reports_ids_only_check_candidates_named_separately():
    check = {"ok": False, "problems": [{"code": "not_canonical", "path": "/alternatives/0/choices/1/value_id",
                                        "candidates": [{"id": "v:2.10", "label": "Quorum"}]}],
             "resolved": [{"id": "d:1"}, {"id": "v:1.1"}, {"id": "s:s1"}]}
    events = _events(_cmd("ddspace query values d:1", "d:1 v:1.1 d:2"),
                     _cmd("ddspace query evidence v:1.1", "s01_p01"),
                     _cmd("ddspace rationale check rationale/kv-explain.json", json.dumps(check), 1))
    audit = runner.fabrication_audit(_with_space(), events)
    assert audit["candidate_only"] == ["v:2.10"]
    assert audit["missing"] == ["s:s1"]              # echoed by check's `resolved`, which returns nothing


def test_fabrication_audit_separates_ids_seen_only_outside_ddspace():
    events = _events(_cmd("ddspace query values d:1", "d:1 v:1.1 d:2 v:2.10 s01_p01"),
                     _cmd("grep attested raw/graph.json", '"attested_by": ["s:s1"]'))
    audit = runner.fabrication_audit(_with_space(), events)
    assert audit["missing"] == [] and audit["other_output_only"] == ["s:s1"]


def test_fabrication_audit_reads_attested_by_entries_that_are_objects():
    doc = _with_space()
    doc["points"][0]["attested_by"] = [{"id": "s:s2", "label": "A source"}, "s:s1", {"label": "x"}]
    events = _events(_cmd("ddspace query values d:1", "d:1 v:1.1 d:2 v:2.10 s01_p01 s:s1"))
    assert "s:s2" in runner.file_ids(doc) and "s:s1" in runner.file_ids(doc)
    audit = runner.fabrication_audit(doc, events)
    assert audit["missing"] == ["s:s2"] and audit["ids"] == 7


# ---------------------------------------------------------------- retrieval misses


GRAPH = {"nodes": [{"id": "d:1", "kind": "dimension", "label": "Data storage", "description": "Where data lives."},
                   {"id": "d:2", "kind": "dimension", "label": "Model monitoring",
                    "description": "How drift is detected."},
                   {"id": "v:1.1", "kind": "value", "label": "Feature store", "dimension_id": "d:1"}],
         "edges": []}


def test_retrieval_miss_lookup_flags_uncovered_items_whose_words_match_a_dimension():
    doc = _with_space(uncovered=[
        {"decision": "Monitoring of the deployed model", "solution_quote": "alerts on drift",
         "nearest_dimension_id": None},
        {"decision": "Team ownership", "solution_quote": "one team owns it", "nearest_dimension_id": None}])
    misses = runner.retrieval_misses(doc, GRAPH)
    assert len(misses) == 1 and misses[0]["path"] == "/uncovered/0"
    found = {(m["id"], m["match"]) for m in misses[0]["matches"]}
    assert ("d:2", "label") in found and not any(m["id"] == "v:1.1" for m in misses[0]["matches"])
    assert "monitoring" in next(m for m in misses[0]["matches"] if m["id"] == "d:2")["words"]
    assert runner.retrieval_misses(_no_space(), GRAPH) == []


# ---------------------------------------------------------------- argv, environment and work copy


def test_n_session_has_ddspace_on_path_and_no_workspace(tmp_path, monkeypatch, cases):
    bin_dir = tmp_path / "envbin"
    bin_dir.mkdir()
    (bin_dir / "ddspace").write_text("")
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-operator-key-000000000")
    s = runner.Session("kv-store", "N", 1)
    workdir = tmp_path / "ws"
    runner.prepare_workdir(s, cases[0], tmp_path / "workspaces", workdir)
    assert sorted(p.name for p in workdir.iterdir()) == ["PROBLEM.md"]
    argv = runner.command(s, workdir, tmp_path / "last.txt", model="gpt-test")
    assert argv[argv.index("-C") + 1] == str(workdir) and "--output-schema" not in argv
    assert controls.NETWORK_ON in argv and controls.WEB_SEARCH_OFF in argv and argv[-1] == "-"   # N describes points too
    env = runner._environment(s, tmp_path / "home", bin_dir / "ddspace", "sk-study-key-000000000",
                              describer="openai/describer")
    assert env["PATH"].split(":")[0] == str(bin_dir) and env["OPENAI_API_KEY"] == "sk-study-key-000000000"
    assert env["DDSPACE_POINT_MODEL"] == "openai/describer" and env["CODEX_HOME"] == str(tmp_path / "home")


@pytest.mark.parametrize("condition", ["E"])
def test_space_sessions_get_network_and_the_study_key(tmp_path, monkeypatch, condition):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-operator-key-000000000")
    s = runner.Session("kv-store", condition, 1)
    argv = runner.command(s, tmp_path / "ws", tmp_path / "last.txt", model="gpt-test")
    assert controls.NETWORK_ON in argv and controls.WEB_SEARCH_OFF in argv and argv[-1] == "-"   # for point descriptions
    env = runner._environment(s, tmp_path / "home", None, "sk-study-key-000000000")
    assert env["OPENAI_API_KEY"] == "sk-study-key-000000000"          # the study key, never the operator's
    assert "OPENAI_API_KEY" not in runner._environment(s, tmp_path / "home", None, None)


def test_space_sessions_get_a_copy_of_their_workspace(tmp_path, cases):
    workspaces = tmp_path / "workspaces"
    (workspaces / "E" / "raw").mkdir(parents=True)
    (workspaces / "E" / "raw" / "graph.json").write_text("{}")
    (workspaces / "E" / ".agents" / "skills" / "old").mkdir(parents=True)
    explain = next(c for c in cases if c["mode"] == "explain")
    s = runner.Session(explain["id"], "E", 1)
    workdir = tmp_path / "ws"
    runner.prepare_workdir(s, explain, workspaces, workdir)
    assert (workdir / "raw" / "graph.json").is_file() and (workdir / "SOLUTION.md").is_file()
    assert not (workdir / ".agents" / "skills" / "old").exists()     # only the runner's skills reach a session


def test_preflight_checks_network_the_manifest_and_the_skill_file(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"files": {"gt_model.json": "abc"}}')
    ws = tmp_path / "ws"
    ws.mkdir()
    # the work copy's manifest may list more inputs (the study's E workspace does); the listed ones must match
    (ws / controls.MANIFEST_COPY).write_text('{"files": {"gt_model.json": "abc", "config.yaml": "def"}}')
    s = runner.Session("kv-store", "E", 1)
    argv = runner.command(s, ws, tmp_path / "last.txt", model="gpt-test")
    assert runner.preflight(s, argv, ws, manifest, model="gpt-test") == []
    at = argv.index(controls.NETWORK_ON)
    no_network = argv[:at - 1] + argv[at + 1:]                          # drop "-c", NETWORK_ON
    assert any("network" in p for p in runner.preflight(s, no_network, ws, manifest, model="gpt-test"))
    n = runner.Session("kv-store", "N", 1)
    n_argv = runner.command(n, tmp_path / "n", tmp_path / "last.txt", model="gpt-test")
    assert runner.preflight(n, n_argv, tmp_path / "n", manifest, model="gpt-test") == []   # N needs network too
    at = n_argv.index(controls.NETWORK_ON)
    assert any("network" in p for p in runner.preflight(n, n_argv[:at - 1] + n_argv[at + 1:], tmp_path / "n",
                                                         manifest, model="gpt-test"))
    assert any("skill" in p for p in runner.preflight(s, argv, ws, manifest, model="gpt-test",
                                                      skill="ddspace-search"))
    for copy in ("{}", '{"files": {"gt_model.json": "other"}}'):
        (ws / controls.MANIFEST_COPY).write_text(copy)
        assert any("manifest" in p for p in runner.preflight(s, argv, ws, manifest, model="gpt-test"))


# ---------------------------------------------------------------- guards


def test_guards_refuse_another_prompt_model_or_skill_delivery(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("## search\nnew\n")
    results = tmp_path / "results"
    (results / "summaries").mkdir(parents=True)
    current = {"model": "gpt-test", "prompt_sha256": controls.sha256(prompt), "skills_via": "files",
               "skills_sha256": runner.skills_sha256()}
    (results / "summaries" / "a-N-r1.json").write_text(json.dumps(current))
    assert runner.guards(results, model="gpt-test", prompt=prompt, skills_via="files") == []
    assert any("model" in g for g in runner.guards(results, model="other", prompt=prompt, skills_via="files"))
    assert any("skill" in g for g in runner.guards(results, model="gpt-test", prompt=prompt, skills_via="prompt"))
    (results / "summaries" / "a-E-r1.json").write_text(json.dumps(dict(current, prompt_sha256="old")))
    refused = runner.guards(results, model="gpt-test", prompt=prompt, skills_via="files")
    assert any("prompt" in g and "a-E-r1" in g for g in refused)


# ---------------------------------------------------------------- skill delivery and the prompt


def test_skills_via_files_writes_the_reference_only_with_a_space(tmp_path):
    texts = {}
    for condition, has_reference in (("E", True), ("N", False)):
        ws = tmp_path / condition
        ws.mkdir()
        extra = runner.deliver_skill(ws, "search", condition, "files")
        folder = ws / ".agents" / "skills" / "ddspace-search"
        texts[condition] = (folder / "SKILL.md").read_text()
        reference = folder / agent.REFERENCE
        assert extra == "" and reference.is_file() == has_reference
        assert not has_reference or "ddspace query" in reference.read_text()
        assert not (ws / ".agents" / "skills" / "ddspace-explain").exists()
    assert texts["E"] == texts["N"] and "ddspace rationale check" in texts["N"]  # one SKILL.md for every condition


def test_skills_via_prompt_appends_the_skill_and_writes_no_file(tmp_path):
    extra = runner.deliver_skill(tmp_path, "explain", "N", "prompt")
    assert not (tmp_path / ".agents").exists()
    assert "name: ddspace-explain" in extra and "ddspace query" not in extra
    assert f"Its {agent.REFERENCE} follows." not in extra                    # N gets no reference
    text = runner.prompt_text(runner.PROMPT, {"id": "kv-explain", "mode": "explain"}, "N", extra)
    assert text.endswith(extra) and "SOLUTION.md" in text and "rationale/kv-explain.json" in text
    with_space = runner.deliver_skill(tmp_path, "explain", "E", "prompt")
    assert with_space.startswith(extra.rstrip("\n")) and f"Its {agent.REFERENCE} follows." in with_space
    assert "ddspace query values" in with_space


def test_the_prompt_differs_across_conditions_only_in_the_space_note():
    case = {"id": "kv-store", "mode": "search"}
    e, n = (runner.prompt_text(runner.PROMPT, case, c) for c in ("E", "N"))
    assert e != n and "ddspace-search" in e and "PROBLEM.md" in e and "{" not in e
    notes = runner.prompt_sections(runner.PROMPT)
    assert e.replace(notes["space"].strip(), "") == n.replace(notes["no space"].strip(), "")


# ---------------------------------------------------------------- a whole session (Codex faked, ddspace real)


@pytest.fixture(autouse=True)
def _codex_through_subprocess_run(monkeypatch):
    """Route the streamed Codex call through ``subprocess.run``, so the tests' fakes of it stand in for Codex."""
    def through_run(argv, *, input, env, timeout, show=print, home="", secrets=()):
        proc = runner.subprocess.run(argv, input=input, capture_output=True, text=True, env=env, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode, False
    monkeypatch.setattr(runner, "run_codex", through_run)


REAL_RUN_CODEX = runner.run_codex


def _fake(monkeypatch, stdout, doc=None, seen=None):
    def fake_run(argv, **kwargs):
        if "exec" in argv and "--json" in argv:                                # the codex session
            if seen is not None:
                seen.update(argv=argv, input=kwargs.get("input"), env=kwargs.get("env"))
            if doc is not None:
                workdir = Path(argv[argv.index("-C") + 1])
                (workdir / "rationale").mkdir(exist_ok=True)
                (workdir / "rationale" / f"{doc['id']}.json").write_text(json.dumps(doc))
            return subprocess.CompletedProcess(argv, 0, stdout, "")
        return REAL_RUN(argv, **kwargs)                         # ddspace rationale check / build
    monkeypatch.setattr(runner.subprocess, "run", fake_run)


def test_a_no_space_session_keeps_the_file_checks_it_and_records_the_build(tmp_path, monkeypatch, cases):
    doc = _no_space()
    doc["alternatives"][0]["choices"][0]["reason"] = f"see {Path.home()}/notes"
    stdout = _jsonl(*_events(_cmd("ddspace rationale check rationale/kv-store.json", '{"ok": true}')))
    seen = {}
    _fake(monkeypatch, stdout, doc, seen)
    case = next(c for c in cases if c["id"] == "kv-store")
    results = tmp_path / "results"
    rec = runner.run(runner.Session("kv-store", "N", 1), case, tmp_path / "workspaces", tmp_path / "scratch",
                     model="gpt-test", results=results, skills_via="prompt",
                     ddspace=[sys.executable, "-m", "delvedspace"])
    assert rec["status"] == "ok", rec["problems"]
    kept = (results / "rationale" / "kv-store-N-r1.json").read_text()
    assert str(Path.home()) not in kept and json.loads(kept)["id"] == "kv-store"
    assert rec["check"]["ok"] is True and rec["check"]["exit_code"] == 0 and rec["check"]["problems"] == []
    assert rec["check_runs"] == 1 and rec["fabrication"]["ids"] == 0
    assert rec["explainer"]["out"] == "explainers/kv-store-N-r1"
    assert rec["explainer"]["exit_code"] == 0, rec["explainer"]   # rendered, with --out inside the results folder
    assert rec["explainer"]["pages"] == ["explainers/kv-store-N-r1/explainers/kv-store.html"]
    assert "name: ddspace-search" in seen["input"] and rec["skills_via"] == "prompt"
    assert not (tmp_path / "scratch" / "kv-store-N-r1").exists()
    saved = json.loads((results / "summaries" / "kv-store-N-r1.json").read_text())
    assert saved["prompt_sha256"] == controls.sha256(runner.PROMPT) and saved["model"] == "gpt-test"


def test_a_session_without_a_rationale_file_fails_and_stays_pending(tmp_path, monkeypatch, cases):
    _fake(monkeypatch, _jsonl(*_events()))
    case = next(c for c in cases if c["id"] == "kv-store")
    s = runner.Session("kv-store", "N", 1)
    rec = runner.run(s, case, tmp_path / "workspaces", tmp_path / "scratch", model="gpt-test",
                     results=tmp_path / "results", ddspace=[sys.executable, "-m", "delvedspace"])
    assert rec["status"] == "failed" and any("rationale/kv-store.json" in p for p in rec["problems"])
    assert runner.pending([s], tmp_path / "results") == [s]


def test_a_failing_check_is_recorded_with_its_codes(tmp_path, monkeypatch, cases):
    doc = _no_space()
    doc["alternatives"] = doc["alternatives"][:1]                 # search needs two to four alternatives
    _fake(monkeypatch, _jsonl(*_events()), doc)
    case = next(c for c in cases if c["id"] == "kv-store")
    rec = runner.run(runner.Session("kv-store", "N", 1), case, tmp_path / "workspaces", tmp_path / "scratch",
                     model="gpt-test", results=tmp_path / "results", ddspace=[sys.executable, "-m", "delvedspace"])
    assert rec["check"]["ok"] is False and rec["check"]["exit_code"] == 1
    assert {"code": "schema", "severity": "error", "path": "/alternatives"} in rec["check"]["problems"]
    assert rec["explainer"]["skipped"] and (tmp_path / "results" / "rationale" / "kv-store-N-r1.json").is_file()


def test_a_rationale_file_that_is_not_utf8_fails_the_session(tmp_path, monkeypatch, cases):
    def fake_run(argv, **kwargs):
        if "exec" in argv and "--json" in argv:
            workdir = Path(argv[argv.index("-C") + 1])
            (workdir / "rationale").mkdir(exist_ok=True)
            (workdir / "rationale" / "kv-store.json").write_bytes(b'{"id": "\xff\xfe"}')
            return subprocess.CompletedProcess(argv, 0, _jsonl(*_events()), "")
        return REAL_RUN(argv, **kwargs)
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    case = next(c for c in cases if c["id"] == "kv-store")
    s = runner.Session("kv-store", "N", 1)
    rec = runner.run(s, case, tmp_path / "workspaces", tmp_path / "scratch", model="gpt-test",
                     results=tmp_path / "results", ddspace=[sys.executable, "-m", "delvedspace"])
    assert rec["status"] == "failed" and any("UTF-8" in p for p in rec["problems"])
    assert runner.pending([s], tmp_path / "results") == [s]


def test_a_space_session_builds_its_explainer_against_the_persistent_workspace(tmp_path, monkeypatch, cases):
    workspaces = tmp_path / "workspaces"
    (workspaces / "E" / "raw").mkdir(parents=True)
    (workspaces / "E" / "raw" / "graph.json").write_text("{}")
    (workspaces / "E" / controls.MANIFEST_COPY).parent.mkdir(parents=True, exist_ok=True)
    (workspaces / "E" / controls.MANIFEST_COPY).write_text(runner.MANIFEST.read_text())
    doc = dict(_no_space(), space={"workspace": "c1", "run": "r", "graph_sha256": "abc"})
    builds = []

    def fake_run(argv, **kwargs):
        if "exec" in argv and "--json" in argv:                    # the codex session
            workdir = Path(argv[argv.index("-C") + 1])
            (workdir / "rationale").mkdir(exist_ok=True)
            (workdir / "rationale" / "kv-store.json").write_text(json.dumps(doc))
            return subprocess.CompletedProcess(argv, 0, _jsonl(*_events()), "")
        if "check" in argv:                                        # ddspace rationale check: clean
            return subprocess.CompletedProcess(argv, 0, json.dumps({"ok": True, "problems": []}), "")
        builds.append((argv, kwargs.get("cwd")))                   # ddspace rationale build
        return subprocess.CompletedProcess(argv, 0, "{}", "")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    case = next(c for c in cases if c["id"] == "kv-store")
    seen = []
    real = fake_run

    def spy(argv, **kwargs):
        if "exec" in argv and "--json" in argv:
            seen.append((argv, kwargs.get("env") or {}))
        return real(argv, **kwargs)
    monkeypatch.setattr(runner.subprocess, "run", spy)
    rec = runner.run(runner.Session("kv-store", "E", 1), case, workspaces, tmp_path / "scratch", model="gpt-test",
                     results=tmp_path / "results", ddspace=["ddspace"], key="sk-study-key-000000000")
    assert rec["status"] == "ok", rec["problems"]
    (argv, env), = seen
    assert controls.NETWORK_ON in argv and env["OPENAI_API_KEY"] == "sk-study-key-000000000"
    (build_argv, build_cwd), = builds
    assert "--graph" in build_argv and build_cwd == str(tmp_path / "results")   # --out must be inside the cwd
    assert build_argv[build_argv.index("--out") + 1] == "explainers/kv-store-E-r1"
    graph = Path(build_argv[build_argv.index("--graph") + 1])
    assert not (tmp_path / "scratch" / "kv-store-E-r1").exists()   # the work copy is gone, the link target is not
    assert graph.is_file() and graph.resolve() == (workspaces / "E" / "raw" / "graph.json").resolve()
    assert rec["explainer"]["links_into"] == "--workspaces/E"


def test_file_ids_are_the_wikis_only():
    """An N file's ids are the agent's own names, not the wiki's: none of them counts as a space id."""
    assert runner.file_ids(_no_space()) == []
    assert {"d:1", "v:1.1", "v:2.10", "s01_p01", "s:s1"} <= set(runner.file_ids(_with_space()))


# ---------------------------------------------------------------- progress while Codex runs


def test_progress_shows_ddspace_commands_file_changes_and_the_end_only():
    cmd = lambda c, code=0: {"type": "item.completed", "item": {  # noqa: E731
        "type": "command_execution", "command": f"/bin/zsh -lc '{c}'", "exit_code": code, "aggregated_output": ""}}
    assert runner.progress(cmd("ddspace query values d:21"), 75) == "    [01:15] ddspace query values d:21"
    assert runner.progress(cmd("ddspace rationale check rationale/x.json", 1), 5).endswith("(exit 1)")
    assert runner.progress(cmd("ls -la"), 5) is None
    assert runner.progress(cmd("cat > rationale/x.json <<EOF"), 5) == "    [00:05] edited the rationale file"
    change = {"type": "item.completed", "item": {"type": "file_change",
                                                 "changes": [{"path": "/w/rationale/x.json", "kind": "add"}]}}
    assert runner.progress(change, 61) == "    [01:01] wrote x.json"
    assert runner.progress({"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}}, 1) is None
    assert runner.progress({"type": "turn.completed"}, 600) == "    [10:00] the agent finished"


def test_run_codex_streams_progress_and_kills_a_session_over_its_timeout(monkeypatch):
    script = ("import json, sys, time\n"
              "sys.stdin.read()\n"
              "print(json.dumps({'type': 'item.completed', 'item': {'type': 'command_execution',"
              " 'command': 'ddspace query dimensions', 'exit_code': 0}}), flush=True)\n"
              "time.sleep(float(sys.argv[1]))\n"
              "print(json.dumps({'type': 'turn.completed'}), flush=True)\n")
    shown = []
    out, err, code, timed_out = REAL_RUN_CODEX([sys.executable, "-c", script, "0"], input="prompt",
                                                 env=dict(os.environ), timeout=30, show=shown.append)
    assert code == 0 and not timed_out and len(out.splitlines()) == 2
    assert [s.split("] ", 1)[1] for s in shown] == ["ddspace query dimensions", "the agent finished"]
    monkeypatch.setattr(runner, "HEARTBEAT", 0)
    monkeypatch.setattr(runner, "POLL", 0.2)
    shown = []
    out, err, code, timed_out = REAL_RUN_CODEX([sys.executable, "-c", script, "30"], input="prompt",
                                                 env=dict(os.environ), timeout=1, show=shown.append)
    assert timed_out and code is None and "ddspace query dimensions" in out
    assert any("still running (1 commands so far)" in s for s in shown)


def test_a_session_gets_an_empty_home_so_personal_skills_stay_out(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "real-home"))
    env = runner._environment(runner.Session("kv-store", "N", 1), tmp_path / "s" / "codex-home", None, None)
    home = Path(env["HOME"])
    assert home == tmp_path / "s" / "home" and home.is_dir() and not any(home.iterdir())
    assert env["CODEX_HOME"] == str(tmp_path / "s" / "codex-home")


def test_points_evaluated_counts_the_file_points_some_ddspace_point_call_took():
    doc = {"points": [{"id": "P1", "values": ["v:1.1", "v:2.1"]}, {"id": "P2", "values": ["v:1.2"]}]}
    calls = [{"values": ["v:2.1", "v:1.1"]}, {"values": ["v:9.9"]}]
    assert runner.points_evaluated(doc, calls) == {"points": 2, "with_ddspace_point": 1, "without": ["P2"]}


def test_the_effort_goes_to_codex_and_one_results_folder_holds_one_effort(tmp_path):
    s = runner.Session("kv-store", "E", 1)
    argv = runner.command(s, tmp_path, tmp_path / "last.txt", model="gpt-test", effort="high")
    assert argv[argv.index('model_reasoning_effort="high"') - 1] == "-c"
    assert 'model_reasoning_effort' not in " ".join(runner.command(s, tmp_path, tmp_path / "l", model="gpt-test"))
    (tmp_path / "results" / "summaries").mkdir(parents=True)
    (tmp_path / "results" / "summaries" / "kv-store-E-r1.json").write_text(json.dumps(
        {"model": "gpt-test", "effort": "medium", "prompt_sha256": controls.sha256(runner.PROMPT),
         "skills_via": "files", "skills_sha256": runner.skills_sha256()}))
    refused = runner.guards(tmp_path / "results", model="gpt-test", prompt=runner.PROMPT, skills_via="files",
                            effort="high")
    assert refused and "reasoning effort" in refused[0]
    assert runner.guards(tmp_path / "results", model="gpt-test", prompt=runner.PROMPT, skills_via="files",
                         effort="medium") == []


def test_the_describer_is_the_e_spaces_model(tmp_path):
    assert runner.describer_model(tmp_path) is None
    (tmp_path / "E" / "raw").mkdir(parents=True)
    (tmp_path / "E" / "raw" / "run.json").write_text('{"models": {"generation_llm": "openai/describer"}}')
    assert runner.describer_model(tmp_path) == "openai/describer"


def test_n_point_calls_count_with_their_names_and_without_the_domain():
    args = ["point", "--no-space", "--domain", "Card fraud", "Serving:  Online", "Store :Feature store"]
    event = controls.point_event(runner._without_domain(args), "{}", True, lambda t: t)
    assert event["values"] == ["Serving:  Online", "Store :Feature store"]
    doc = {"points": [{"id": "P1", "values": ["Serving: Online", "Store: Feature store"]},
                      {"id": "P2", "values": ["Serving: Batch"]}]}
    assert runner.points_evaluated(doc, [event]) == {"points": 2, "with_ddspace_point": 1, "without": ["P2"]}


def test_ddspace_calls_split_only_outside_quotes():
    script = ("ddspace point --no-space 'Release: Shadow; then promote' \\\n  \"Store: A && B\" && "
              "ddspace rationale check r.json; echo done | cat\nddspace point v:1.1")
    assert runner._ddspace_calls(script) == [
        ["point", "--no-space", "Release: Shadow; then promote", "Store: A && B"],
        ["rationale", "check", "r.json"], ["point", "v:1.1"]]


# ---------------------------------------------------------------- the E workspace builder

builder = _load("build_workspace")


def test_the_tracked_inputs_match_their_manifest():
    assert builder.verify() == []
    inputs = runner.MANIFEST.parent
    assert json.loads(runner.MANIFEST.read_text())["files"] == {
        name: controls.sha256(inputs / name) for name in ("gt_model.json", "dimension_names.yaml")}


def test_every_decision_gets_a_dimension_name_and_keeps_its_question():
    import yaml
    inputs = runner.MANIFEST.parent
    model = json.loads((inputs / "gt_model.json").read_text())
    names = yaml.safe_load((inputs / "dimension_names.yaml").read_text())
    named = builder.named_model(model, names)
    assert len(named["decisions"]) == len(model["decisions"]) == 28
    for before, after in zip(model["decisions"], named["decisions"]):
        assert after["id"] == before["id"] and after["description"] == before["question"]   # the authors' words
        assert after["name"] == names[before["id"]] and "?" not in after["name"]            # a concern, not a question
    assert len({d["name"] for d in named["decisions"]}) == 28                                  # all distinct
    assert model["decisions"][0]["name"].endswith("?")                                         # the input is unchanged
    with pytest.raises(ValueError, match="missing"):
        builder.named_model(model, dict(list(names.items())[1:]))
    with pytest.raises(ValueError, match="unknown"):
        builder.named_model(model, dict(names, extra_decision="Extra"))


def test_the_builder_refuses_changed_inputs(tmp_path):
    (tmp_path / "gt_model.json").write_text("{}")
    (tmp_path / "manifest.json").write_text('{"files": {"gt_model.json": "abc"}}')
    assert builder.verify(tmp_path) == ["gt_model.json"]
    with pytest.raises(ValueError, match="gt_model.json"):
        builder.build(tmp_path / "out", tmp_path)


# ---------------------------------------------------------------- the paper's numbers

analysis = _load("analyze")
PAPER = {   # Table 1 and the counts in the text, as the paper rounds them
    "E": {"operations": 41, "points": 8.4, "dimensions_per_point": 8.4, "alternatives": 3.1, "strong_share": 0.24,
          "tradeoffs_per_step": 1.1, "values_per_cause": 2.3, "requirements_per_tradeoff": 3.6, "unaddressed": 2.8,
          "uncovered": 5.0, "shared_values": 0.51, "unaddressed_total": 34, "unaddressed_constraints": 20,
          "evidence_absence_share": 0.24, "sessions": 12},
    "N": {"operations": 18, "points": 10.0, "dimensions_per_point": 4.9, "alternatives": 3.4, "strong_share": 0.62,
          "tradeoffs_per_step": 1.1, "values_per_cause": 1.7, "requirements_per_tradeoff": 3.1, "unaddressed": 0,
          "uncovered": 0, "shared_values": 0.01, "unaddressed_total": 0, "unaddressed_constraints": 0,
          "evidence_absence_share": 0.06, "sessions": 12},
}


def test_analyze_recomputes_the_papers_numbers_from_the_second_run():
    numbers = analysis.analyze(ROOT / "study" / "designing2027" / "results-v2", ["E", "N"])
    for condition, expected in PAPER.items():
        for key, value in expected.items():
            got = numbers[condition][key]
            digits = 2 if isinstance(value, float) and value < 1 else 1
            assert round(got, digits) == value if isinstance(value, float) else round(got) == value, (condition, key)


def test_analyze_renders_every_row_of_the_table():
    text = analysis.render(analysis.analyze(ROOT / "study" / "designing2027" / "results-v2", ["E", "N"]))
    assert all(label in text for _, label, _ in analysis.ROWS) and "51%" in text and "62%" in text
