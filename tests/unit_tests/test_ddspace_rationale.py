"""ddspace rationale check: the ddspace-rationale/1 file, its structural rules and its rules against a space."""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from delvedspace import cli, rationale
from delvedspace.workspace import Workspace
from taxonomy_generator.wiki import build, write
from taxonomy_generator.wiki import query as q
from tests.unit_tests.test_wiki_export import POINTS, _inputs

SAMPLE = Path(__file__).resolve().parent / "fixtures" / "rationale_search.json"
runner = CliRunner()


def _invoke(*args):
    return runner.invoke(cli.app, list(args))


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A workspace whose wiki is the synthetic toy export; the current folder is its root."""
    root = tmp_path / "proj" / "space"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    write(build(_inputs(design_points=POINTS)), root, "toy")
    monkeypatch.chdir(root)
    return Workspace(root)


@pytest.fixture
def graph(ws):
    return q.load(ws.root / "raw" / "graph.json")


def _sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def _check(doc, graph=None):
    sha = None if graph is None else hashlib.sha256(
        (Path.cwd() / "raw" / "graph.json").read_bytes()).hexdigest()
    return rationale.check(doc, graph, sha)


def _codes(result):
    return {(p["code"], p["path"]) for p in result["problems"]}


def _explain(uncovered=2):
    doc = _sample()
    doc.update(id="toy-store-explain", mode="explain", comparison=[])
    alt = doc["alternatives"][0]
    alt["id"] = "S"
    for choice, quote in zip(alt["choices"], ["data stays on each node's disk", "a three-phase commit"]):
        choice["solution_quote"] = quote
    doc["alternatives"] = [alt]
    doc["uncovered"] = [
        {"decision": "Backup schedule", "solution_quote": "nightly snapshots", "nearest_dimension_id": "d:1"},
        {"decision": "Client library", "solution_quote": "a Go client", "nearest_dimension_id": None},
    ][:uncovered]
    return doc


def _no_space(mode="search"):
    alt = lambda i, opts: {  # noqa: E731
        "id": i, "name": i, "summary": "",
        "choices": [{"decision": d, "option": o, "drivers": ["Q1"], "reason": "r", "solution_quote": None}
                    for d, o in opts],
        "considered": [{"decision": "Store", "option": "Postgres", "drivers": ["C1"], "reason": "too heavy"}],
        "open": [{"decision": "Replication", "reason": "no requirement decides it"}],
        "relations": [{"source": "Store", "target": "Replication", "type": "constrains", "holds": True,
                       "note": ""}],
    }
    doc = _sample()
    doc.update(space=None, alternatives=[alt("A1", [("Store", "Local disks")]), alt("A2", [("Store", "S3")])],
               comparison=[{"decision": "Store", "note": "disks versus S3"}])
    return doc


# ---------------------------------------------------------------- clean files


def test_the_shared_sample_is_clean_and_echoes_labels(graph):
    result = _check(_sample(), graph)
    assert result["ok"] and result["problems"] == [], result["problems"]
    assert result["graph_sha256"] == _sample()["space"]["graph_sha256"]
    labels = {r["id"]: r["label"] for r in result["resolved"]}
    assert labels["d:1"] == "Source of truth" and labels["v:1.1"] == "Disk quorum"
    assert labels["v:2.1"] == "Three-phase commit" and labels["v:1.2"] == "WAL in S3"
    assert len(result["resolved"]) == len(labels)  # each id once


def test_a_valid_explain_file_is_clean(graph):
    result = _check(_explain(), graph)
    assert result["ok"] and result["problems"] == [], result["problems"]


def test_the_cli_checks_the_sample_in_a_workspace(ws):
    result = _invoke("rationale", "check", str(SAMPLE))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["ok"] and payload["problems"] == []
    assert {"id": "v:1.1", "label": "Disk quorum"} in payload["resolved"]


# ---------------------------------------------------------------- structure


@pytest.mark.parametrize("count", [1, 5])
def test_search_needs_two_to_four_alternatives(graph, count):
    doc = _sample()
    doc["alternatives"] = [dict(copy.deepcopy(doc["alternatives"][0]), id=f"A{i}") for i in range(count)]
    assert ("schema", "/alternatives") in _codes(_check(doc, graph))


def test_explain_has_exactly_one_alternative_named_s(graph):
    doc = _explain()
    doc["alternatives"].append(dict(copy.deepcopy(doc["alternatives"][0]), id="T"))
    assert ("schema", "/alternatives") in _codes(_check(doc, graph))
    doc = _explain()
    doc["alternatives"][0]["id"] = "A1"
    assert ("schema", "/alternatives/0/id") in _codes(_check(doc, graph))


def test_explain_choices_need_a_solution_quote(graph):
    doc = _explain()
    doc["alternatives"][0]["choices"][1]["solution_quote"] = None
    assert ("schema", "/alternatives/0/choices/1/solution_quote") in _codes(_check(doc, graph))


def test_a_missing_field_is_a_schema_error(graph):
    doc = _sample()
    del doc["problem"]["requirements"]
    del doc["alternatives"][1]["choices"][0]["value_id"]
    result = _check(doc, graph)
    assert {("schema", "/problem/requirements"),
            ("schema", "/alternatives/1/choices/0/value_id")} <= _codes(result)
    assert not result["ok"] and all(p["severity"] == "error" for p in result["problems"])


def test_a_wrong_schema_tag_or_mode_is_a_schema_error():
    doc = _no_space()
    doc["schema"], doc["mode"] = "ddspace-rationale/0", "browse"
    assert {("schema", "/schema"), ("schema", "/mode")} <= _codes(rationale.check(doc))


def test_no_space_file_runs_the_structural_rules_only():
    result = rationale.check(_no_space())
    assert result == {"ok": True, "graph_sha256": None, "problems": [], "resolved": []}


def test_no_space_two_options_for_one_decision(graph):
    doc = _no_space()
    doc["alternatives"][0]["choices"].append(
        {"decision": " store", "option": "Both", "drivers": [], "reason": "", "solution_quote": None})
    assert ("two_values_one_dimension", "/alternatives/0/choices/1") in _codes(rationale.check(doc))


def test_no_space_explain_with_uncovered_items_is_a_schema_error():
    doc = _no_space()
    doc["mode"] = "explain"
    alt = doc["alternatives"][0]
    alt["id"] = "S"
    alt["choices"][0]["solution_quote"] = "local disks"
    doc["alternatives"], doc["comparison"] = [alt], []
    doc["uncovered"] = [{"decision": "Backups", "solution_quote": "nightly", "nearest_dimension_id": None}]
    assert ("schema", "/uncovered") in _codes(rationale.check(doc))
    doc["uncovered"] = []
    assert rationale.check(doc)["problems"] == []


def test_no_space_still_checks_requirement_links():
    doc = _no_space()
    doc["alternatives"][1]["choices"][0]["drivers"] = ["Q1", "X9"]
    assert ("unknown_requirement", "/alternatives/1/choices/0/drivers/1") in _codes(rationale.check(doc))


# ---------------------------------------------------------------- rules against the space


def test_unknown_id_lists_candidates(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["value_id"] = "v:9.9"
    doc["alternatives"][1]["open"][0]["dimension_id"] = "Replicaton"
    result = _check(doc, graph)
    assert {("unknown_id", "/alternatives/0/choices/0/value_id"),
            ("unknown_id", "/alternatives/1/open/0/dimension_id")} <= _codes(result)
    typo = next(p for p in result["problems"] if p["path"] == "/alternatives/1/open/0/dimension_id")
    assert typo["candidates"][0]["id"] == "d:2"


@pytest.mark.parametrize("ref", ["1.1", "Disk quorum", "v:1.1 "])
def test_a_bare_id_or_label_is_not_canonical(graph, ref):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["value_id"] = ref
    result = _check(doc, graph)
    problem = next(p for p in result["problems"] if p["code"] == "not_canonical")
    assert problem["path"] == "/alternatives/0/choices/0/value_id"
    assert problem["candidates"][0]["id"] == "v:1.1" and "v:1.1" in problem["message"]
    assert not result["ok"]


def test_value_not_in_dimension(graph):
    doc = _sample()
    doc["alternatives"][1]["choices"][0]["value_id"] = "v:2.2"
    assert ("value_not_in_dimension", "/alternatives/1/choices/0/value_id") in _codes(_check(doc, graph))
    doc = _sample()
    doc["alternatives"][0]["considered"][0]["value_id"] = "v:2.3"
    assert ("value_not_in_dimension", "/alternatives/0/considered/0/value_id") in _codes(_check(doc, graph))


def test_two_values_of_one_dimension(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"].append(
        {"dimension_id": "d:1", "value_id": "v:1.2", "drivers": ["C1"], "reason": "", "evidence": [],
         "solution_quote": None})
    assert ("two_values_one_dimension", "/alternatives/0/choices/2") in _codes(_check(doc, graph))


def test_unknown_requirement(graph):
    doc = _sample()
    doc["alternatives"][0]["considered"][0]["drivers"] = ["Q9"]
    assert ("unknown_requirement", "/alternatives/0/considered/0/drivers/0") in _codes(_check(doc, graph))


def test_evidence_not_on_value(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["evidence"].append({"doc": "s02_p01", "stance": "accepts"})
    assert ("evidence_not_on_value", "/alternatives/0/choices/0/evidence/1") in _codes(_check(doc, graph))


@pytest.mark.parametrize("claim", [{"type": "requires"}, {"source": "d:2", "target": "d:1"}])
def test_relation_mismatch_on_type_or_direction(graph, claim):
    doc = _sample()
    doc["alternatives"][0]["relations"][0].update(claim)
    result = _check(doc, graph)
    problem = next(p for p in result["problems"] if p["code"] == "relation_mismatch")
    assert problem["path"] == "/alternatives/0/relations/0" and problem["severity"] == "error"
    assert problem["candidates"] == [{"source": "d:1", "target": "d:2", "type": "constrains", "directed": True}]


def test_a_relation_missing_from_the_graph(graph):
    doc = _sample()
    doc["alternatives"][0]["relations"][0].update(source="d:1", target="d:1")
    assert ("relation_mismatch", "/alternatives/0/relations/0") in _codes(_check(doc, graph))


def test_ids_in_comparison_and_uncovered_are_checked(graph):
    doc = _explain()
    doc["uncovered"][0]["nearest_dimension_id"] = "2"
    assert ("not_canonical", "/uncovered/0/nearest_dimension_id") in _codes(_check(doc, graph))
    doc = _sample()
    doc["comparison"][1]["dimension_id"] = "v:2.1"  # a value, not a dimension
    assert ("unknown_id", "/comparison/1/dimension_id") in _codes(_check(doc, graph))


# ---------------------------------------------------------------- warnings and the command


def _graph_with_requires(ws, tmp_path):
    data = json.loads((ws.root / "raw" / "graph.json").read_text(encoding="utf-8"))
    data["edges"].append({"source": "d:1", "target": "d:2", "type": "relation", "relation": "requires",
                          "directed": True, "reading": "Source of truth requires a choice on Replication"})
    path = tmp_path / "requires" / "raw" / "graph.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_unmet_requires_is_a_warning(ws, tmp_path):
    path = _graph_with_requires(ws, tmp_path)
    doc = _sample()
    doc["space"]["graph_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    file = tmp_path / "r.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    result = _invoke("rationale", "check", str(file), "--graph", str(path.parent.parent))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["ok"]
    assert [(p["code"], p["path"], p["severity"]) for p in payload["problems"]] == [
        ("unmet_requires", "/alternatives/1", "warning")]  # A1 picks both dimensions; A2 leaves Replication open


def test_a_changed_graph_is_a_warning(ws, tmp_path):
    doc = _sample()
    doc["space"]["graph_sha256"] = "0" * 64
    file = tmp_path / "r.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["ok"] and payload["graph_sha256"] == _sample()["space"]["graph_sha256"]
    assert [(p["code"], p["path"], p["severity"]) for p in payload["problems"]] == [
        ("graph_changed", "/space/graph_sha256", "warning")]


def test_errors_exit_1_with_the_problems(ws, tmp_path):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["value_id"] = "1.1"
    file = tmp_path / "r.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert not payload["ok"] and payload["problems"][0]["code"] == "not_canonical"


def test_no_space_file_outside_a_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "r.json"
    file.write_text(json.dumps(_no_space()), encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"ok": True, "graph_sha256": None, "problems": [], "resolved": []}
    doc = _no_space()
    doc["alternatives"][0]["choices"].append(dict(doc["alternatives"][0]["choices"][0], option="S3"))
    file.write_text(json.dumps(doc), encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 1
    assert json.loads(result.stdout)["problems"][0]["code"] == "two_values_one_dimension"


def test_a_named_space_without_a_graph_exits_2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = _invoke("rationale", "check", str(SAMPLE))
    assert result.exit_code == 2
    assert "error" in json.loads(result.stdout)
    result = _invoke("rationale", "check", str(SAMPLE), "--graph", str(tmp_path / "nowhere"))
    assert result.exit_code == 2 and "error" in json.loads(result.stdout)


def test_malformed_or_missing_file_exits_2(ws, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    for path in (bad, tmp_path / "missing.json"):
        result = _invoke("rationale", "check", str(path))
        assert result.exit_code == 2, result.output
        assert "error" in json.loads(result.stdout)


def test_a_file_that_is_not_an_object_is_a_schema_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "r.json"
    file.write_text("[]", encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 1
    assert json.loads(result.stdout)["problems"][0] == {
        "code": "schema", "severity": "error", "path": "", "message": "expected an object, got list",
        "candidates": []}


def test_table_prints_a_readable_problem_table(ws, tmp_path):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["value_id"] = "1.1"
    file = tmp_path / "r.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    result = _invoke("rationale", "check", str(file), "--table")
    assert result.exit_code == 1
    assert "not_canonical" in result.output and "/alternatives/0/choices/0/value_id" in result.output
    assert "Disk quorum" in result.output and not result.output.lstrip().startswith("{")
    clean = _invoke("rationale", "check", str(SAMPLE), "--table")
    assert clean.exit_code == 0 and "no problems" in clean.output.lower()
