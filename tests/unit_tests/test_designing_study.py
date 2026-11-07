"""study/designing2027: the session runner for the rationale search and explain study (M, E and N)."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"designing_{name}", ROOT / "study" / "designing2027" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # dataclasses look their module up while the class is built
    spec.loader.exec_module(module)
    return module


runner = _load("run_sessions")
cain = runner.cain
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
    """A clean no-space search file (space: null), as an N session writes it."""
    choice = {"decision": "Storage", "option": "Local disks", "drivers": ["Q1"], "reason": "Survives a node failure."}
    other = {"decision": "Storage", "option": "Log in S3", "drivers": ["Q1"], "reason": "S3 is already there."}
    return {"schema": "ddspace-rationale/1", "id": case_id, "mode": "search", "space": None,
            "problem": {"title": "A store", "requirements": [{"id": "Q1", "text": "No committed write is lost."}]},
            "alternatives": [{"id": "A1", "name": "Disks", "choices": [choice]},
                             {"id": "A2", "name": "S3", "choices": [other]}],
            "uncovered": []}


def _with_space(uncovered=()):
    """An explain file with ids, a passage, a source and uncovered items (not checked against a graph here)."""
    return {"schema": "ddspace-rationale/1", "id": "kv-explain", "mode": "explain",
            "space": {"workspace": "c1", "run": "r", "graph_sha256": "abc"},
            "problem": {"title": "A store", "requirements": [{"id": "Q1", "text": "No write is lost."}]},
            "alternatives": [{"id": "S", "name": "The solution", "choices": [
                {"dimension_id": "d:1", "value_id": "v:1.1", "drivers": ["Q1"], "reason": "r",
                 "evidence": [{"doc": "s01_p01", "stance": "accepts"}], "solution_quote": "local disks"},
                {"dimension_id": "d:2", "value_id": "v:2.10", "drivers": ["Q1"], "reason": "r",
                 "solution_quote": "a quorum"}],
                "point": {"attested_by": ["s:s1"]}}],
            "uncovered": list(uncovered)}


# ---------------------------------------------------------------- plan, resume and cases


def test_plan_is_case_by_condition_by_repetition_and_resume_skips_finished(cases, tmp_path):
    planned = runner.plan(cases, ["M", "E", "N"], 2)
    assert len(planned) == 24 and len({s.id for s in planned}) == 24
    assert planned[0].id == "feed-M-r1" and planned[0].case == "feed"   # cases in folder order
    results = tmp_path / "results"
    (results / "rationale").mkdir(parents=True)
    (results / "rationale" / "kv-store-M-r1.json").write_text("{}")
    (results / "summaries").mkdir()
    (results / "summaries" / "kv-store-E-r1.json").write_text("{}")   # a summary alone: the session failed
    left = runner.pending(planned, results)
    assert len(left) == 23 and "kv-store-M-r1" not in {s.id for s in left}


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
    assert cain.NETWORK_ON not in argv and cain.WEB_SEARCH_OFF in argv and argv[-1] == "-"
    env = runner._environment(s, tmp_path / "home", bin_dir / "ddspace")
    assert env["PATH"].split(":")[0] == str(bin_dir) and "OPENAI_API_KEY" not in env
    assert env["CODEX_HOME"] == str(tmp_path / "home")


def test_space_sessions_get_a_copy_of_their_workspace_and_no_network(tmp_path, cases):
    workspaces = tmp_path / "workspaces"
    (workspaces / "M" / "raw").mkdir(parents=True)
    (workspaces / "M" / "raw" / "graph.json").write_text("{}")
    (workspaces / "M" / ".agents" / "skills" / "old").mkdir(parents=True)
    explain = next(c for c in cases if c["mode"] == "explain")
    s = runner.Session(explain["id"], "M", 1)
    workdir = tmp_path / "ws"
    runner.prepare_workdir(s, explain, workspaces, workdir)
    assert (workdir / "raw" / "graph.json").is_file() and (workdir / "SOLUTION.md").is_file()
    assert not (workdir / ".agents" / "skills" / "old").exists()     # only the runner's skills reach a session
    argv = runner.command(s, workdir, tmp_path / "last.txt", model="gpt-test")
    assert cain.NETWORK_ON not in argv                                # point --no-llm needs no network


def test_preflight_checks_network_the_manifest_and_the_skill_file(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"files": {}}')
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / cain.MANIFEST_COPY).write_text(manifest.read_text())
    s = runner.Session("kv-store", "M", 1)
    argv = runner.command(s, ws, tmp_path / "last.txt", model="gpt-test")
    assert runner.preflight(s, argv, ws, manifest, model="gpt-test") == []
    assert any("network" in p for p in runner.preflight(s, argv + ["-c", cain.NETWORK_ON], ws, manifest,
                                                         model="gpt-test"))
    assert any("skill" in p for p in runner.preflight(s, argv, ws, manifest, model="gpt-test",
                                                      skill="ddspace-search"))
    (ws / cain.MANIFEST_COPY).write_text("{}")
    assert any("manifest" in p for p in runner.preflight(s, argv, ws, manifest, model="gpt-test"))


# ---------------------------------------------------------------- guards


def test_guards_refuse_another_prompt_model_or_skill_delivery(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("## search\nnew\n")
    results = tmp_path / "results"
    (results / "summaries").mkdir(parents=True)
    current = {"model": "gpt-test", "prompt_sha256": cain.design.sha256(prompt), "skills_via": "files",
               "skills_sha256": runner.skills_sha256()}
    (results / "summaries" / "a-N-r1.json").write_text(json.dumps(current))
    assert runner.guards(results, model="gpt-test", prompt=prompt, skills_via="files") == []
    assert any("model" in g for g in runner.guards(results, model="other", prompt=prompt, skills_via="files"))
    assert any("skill" in g for g in runner.guards(results, model="gpt-test", prompt=prompt, skills_via="prompt"))
    (results / "summaries" / "a-M-r1.json").write_text(json.dumps(dict(current, prompt_sha256="old")))
    refused = runner.guards(results, model="gpt-test", prompt=prompt, skills_via="files")
    assert any("prompt" in g and "a-M-r1" in g for g in refused)


# ---------------------------------------------------------------- skill delivery and the prompt


def test_skills_via_files_writes_the_variant_of_the_condition(tmp_path):
    for condition, has_query in (("M", True), ("N", False)):
        ws = tmp_path / condition
        ws.mkdir()
        extra = runner.deliver_skill(ws, "search", condition, "files")
        text = (ws / ".agents" / "skills" / "ddspace-search" / "SKILL.md").read_text()
        assert extra == "" and ("ddspace query" in text) == has_query and "ddspace rationale check" in text
        assert not (ws / ".agents" / "skills" / "ddspace-explain").exists()


def test_skills_via_prompt_appends_the_skill_and_writes_no_file(tmp_path):
    extra = runner.deliver_skill(tmp_path, "explain", "N", "prompt")
    assert not (tmp_path / ".agents").exists()
    assert "name: ddspace-explain" in extra and "ddspace query" not in extra
    text = runner.prompt_text(runner.PROMPT, {"id": "kv-explain", "mode": "explain"}, "N", extra)
    assert text.endswith(extra) and "SOLUTION.md" in text and "rationale/kv-explain.json" in text


def test_the_prompt_differs_across_conditions_only_in_the_space_note():
    case = {"id": "kv-store", "mode": "search"}
    m, e, n = (runner.prompt_text(runner.PROMPT, case, c) for c in ("M", "E", "N"))
    assert m == e and m != n and "ddspace-search" in m and "PROBLEM.md" in m and "{" not in m
    notes = runner.prompt_sections(runner.PROMPT)
    assert m.replace(notes["space"].strip(), "") == n.replace(notes["no space"].strip(), "")


# ---------------------------------------------------------------- a whole session (Codex faked, ddspace real)


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
    assert rec["explainer"]["exit_code"] is not None             # built, or the error of a missing command
    assert "name: ddspace-search" in seen["input"] and rec["skills_via"] == "prompt"
    assert not (tmp_path / "scratch" / "kv-store-N-r1").exists()
    saved = json.loads((results / "summaries" / "kv-store-N-r1.json").read_text())
    assert saved["prompt_sha256"] == cain.design.sha256(runner.PROMPT) and saved["model"] == "gpt-test"


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
