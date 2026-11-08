"""ddspace rationale check: the ddspace-rationale/4 file, its structural rules and its rules against a space."""

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
    del doc["approaches"]
    alt = doc["alternatives"][0]
    del alt["approach"]
    alt["id"] = "S"
    for choice, quote, forced in zip(alt["choices"], ["data stays on each node's disk", "a three-phase commit"],
                                     [True, None]):
        choice["solution_quote"], choice["forced"] = quote, forced
    alt["step"] = 1
    doc["alternatives"] = [alt]
    doc["budget"] = {"max_points": 8}
    doc["trajectory"] = [
        {"step": 1, "move": "solution", "parent": None, "values": ["v:1.1", "v:2.1"],
         "hypothesis": "The solution as one design point.", "assessment": {"R1": "meets", "Q1": "meets"},
         "observation": "A source attests the whole point.", "verdict": "grounded",
         "point": {"description": "Local disks with a quorum and a commit protocol.", "attested_by": ["s:s1"]}},
        {"step": 2, "move": "region", "parent": 1, "values": ["v:1.1"],
         "hypothesis": "Durability alone calls for the disk quorum.", "assessment": {"Q1": "meets"},
         "observation": "Attested on its own.", "verdict": "grounded",
         "point": {"description": "Local disks with a quorum.", "attested_by": ["s:s1"]}},
    ]
    doc["regions"] = [{"id": "G1", "name": "Disk quorum", "values": ["v:1.1"], "step": 2, "drivers": ["Q1"],
                       "reason": "Durability on one node failure forces a quorum of local disks."}]
    doc["adrs"] = [
        {"id": "ADR1", "title": "Where the truth lives", "drivers": ["Q1"], "context": "c", "options": [
            {"id": "O1", "name": "Disk quorum", "values": ["v:1.1"], "status": "chosen", "in": ["S"], "step": 2,
             "pros": ["survives a node failure"], "cons": [], "reason": "r"},
            {"id": "O2", "name": "WAL in S3", "values": ["v:1.2"], "status": "discarded", "pros": [], "cons": ["c"],
             "reason": "r"}]},
        {"id": "ADR2", "title": "How replicas agree", "drivers": ["R1"], "context": "c", "options": [
            {"id": "O1", "name": "Three-phase commit", "values": ["v:2.1"], "status": "chosen", "in": ["S"],
             "pros": [], "cons": [], "reason": "r"}]}]
    doc["uncovered"] = [
        {"decision": "Backup schedule", "solution_quote": "nightly snapshots", "nearest_dimension_id": "d:1"},
        {"decision": "Client library", "solution_quote": "a Go client", "nearest_dimension_id": None},
    ][:uncovered]
    return doc


OWN_SPACE = {
    "dimensions": [
        {"id": "d:1", "name": "Store", "values": [{"id": "v:1.1", "name": "Local disks"}, {"id": "v:1.2", "name": "S3"},
                                                  {"id": "v:1.3", "name": "Postgres"}]},
        {"id": "d:2", "name": "Replication", "values": [{"id": "v:2.1", "name": "Quorum"},
                                                        {"id": "v:2.2", "name": "None"}]},
    ],
    "relations": [{"source": "d:1", "target": "d:2", "type": "constrains"}],
}


def _own():
    """A search file with the agent's own space (no wiki)."""
    alt = lambda i, approach, step, value: {  # noqa: E731
        "id": i, "name": i, "summary": "", "approach": approach, "step": step,
        "choices": [{"dimension_id": "d:1", "value_id": value, "drivers": ["Q1"], "reason": "r"}],
        "considered": [{"dimension_id": "d:1", "value_id": "v:1.3", "drivers": ["C1"], "reason": "too heavy"}],
        "open": [{"dimension_id": "d:2", "reason": "no requirement decides it"}],
        "relations": [{"source": "d:1", "target": "d:2", "type": "constrains", "holds": True, "note": ""}],
    }
    step = lambda n, move, approach, value: {  # noqa: E731
        "step": n, "round": 1, "approach": approach, "move": move, "parent": None, "values": [value],
        "hypothesis": "h", "assessment": {"Q1": "meets"}, "observation": "o", "rating": "strong"}
    doc = _sample()
    doc.update(space=copy.deepcopy(OWN_SPACE),
               approaches=[{"id": "A", "idea": "what if disks?", "status": "live"},
                           {"id": "B", "idea": "what if S3?", "status": "live"}],
               alternatives=[alt("A1", "A", 1, "v:1.1"), alt("A2", "B", 2, "v:1.2")],
               trajectory=[step(1, "seed", "A", "v:1.1"), step(2, "seed", "B", "v:1.2")],
               adrs=[{"id": "ADR1", "title": "Store", "drivers": ["Q1"], "context": "c", "options": [
                   {"id": "O1", "name": "Local disks", "values": ["v:1.1"], "status": "chosen", "in": ["A1"],
                    "pros": ["p"], "cons": ["c"], "reason": "r"},
                   {"id": "O2", "name": "S3", "values": ["v:1.2"], "status": "chosen", "in": ["A2"],
                    "pros": ["p"], "cons": ["c"], "reason": "r"},
                   {"id": "O3", "name": "Postgres", "values": ["v:1.3"], "status": "discarded",
                    "pros": [], "cons": ["too heavy"], "reason": "r"}]}],
               comparison=[{"dimension_id": "d:1", "note": "disks versus S3"}])
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
    doc = _own()
    doc["schema"], doc["mode"] = "ddspace-rationale/3", "browse"
    assert {("schema", "/schema"), ("schema", "/mode")} <= _codes(rationale.check(doc))


def test_an_own_space_file_is_checked_against_its_own_space():
    result = rationale.check(_own())
    assert result["ok"] and result["problems"] == [] and result["graph_sha256"] is None, result["problems"]
    labels = {r["id"]: r["label"] for r in result["resolved"]}
    assert labels["d:1"] == "Store" and labels["v:1.2"] == "S3"


def test_an_own_space_needs_its_ids(graph):
    doc = _own()
    doc["trajectory"][0]["values"] = ["v:1.9"]
    doc["alternatives"][0]["choices"][0]["value_id"] = "v:2.1"   # a value of Replication, not of Store
    doc["alternatives"][1]["open"][0]["dimension_id"] = "d:3"
    codes = _codes(rationale.check(doc))
    assert ("unknown_id", "/trajectory/0/values/0") in codes
    assert ("value_not_in_dimension", "/alternatives/0/choices/0/value_id") in codes
    assert ("unknown_id", "/alternatives/1/open/0/dimension_id") in codes
    problem = next(p for p in rationale.check(doc)["problems"] if p["path"] == "/trajectory/0/values/0")
    assert "v:1.1" in [c["id"] for c in problem["candidates"]]


def test_an_own_space_is_well_formed():
    doc = _own()
    doc["space"]["dimensions"][1]["values"][0]["id"] = "v:1.1"   # the same id twice
    doc["space"]["dimensions"].append({"id": "d:3", "name": "Empty", "values": []})
    doc["space"]["relations"].append({"source": "d:1", "target": "d:7", "type": "requires"})
    codes = _codes(rationale.check(doc))
    assert ("schema", "/space/dimensions/1/values/0/id") in codes
    assert ("schema", "/space/dimensions/2/values") in codes
    assert ("unknown_id", "/space/relations/1/target") in codes


def test_an_own_space_relation_claim_must_be_in_its_relations():
    doc = _own()
    doc["alternatives"][0]["relations"][0]["type"] = "requires"
    assert ("relation_mismatch", "/alternatives/0/relations/0") in _codes(rationale.check(doc))


def test_own_space_two_values_for_one_dimension():
    doc = _own()
    doc["alternatives"][0]["choices"].append(
        {"dimension_id": "d:1", "value_id": "v:1.3", "drivers": [], "reason": ""})
    assert ("two_values_one_dimension", "/alternatives/0/choices/1") in _codes(rationale.check(doc))


def test_own_space_explain_with_uncovered_items_is_a_schema_error():
    doc = _own()
    doc["mode"] = "explain"
    del doc["approaches"]
    alt = doc["alternatives"][0]
    del alt["approach"]
    alt["id"] = "S"
    alt["choices"][0].update(solution_quote="local disks", forced=None)
    doc["alternatives"], doc["comparison"] = [alt], []
    step = doc["trajectory"][0]
    for key in ("round", "approach", "rating"):
        del step[key]
    doc["trajectory"] = [dict(step, move="solution", verdict="grounded")]
    doc["regions"] = [{"id": "G1", "name": "Local disks", "values": ["v:1.1"], "step": 1, "drivers": ["Q1"],
                       "reason": "r"}]
    doc["adrs"][0]["options"] = [dict(doc["adrs"][0]["options"][0], **{"in": ["S"]}), doc["adrs"][0]["options"][2]]
    doc["uncovered"] = [{"decision": "Backups", "solution_quote": "nightly", "nearest_dimension_id": None}]
    assert ("schema", "/uncovered") in _codes(rationale.check(doc))
    doc["uncovered"] = []
    assert rationale.check(doc)["problems"] == []


def test_own_space_still_checks_requirement_links():
    doc = _own()
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


def test_an_own_space_file_outside_a_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "r.json"
    file.write_text(json.dumps(_own()), encoding="utf-8")
    result = _invoke("rationale", "check", str(file))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["ok"] and payload["graph_sha256"] is None and payload["problems"] == []
    doc = _own()
    doc["alternatives"][0]["choices"].append(dict(doc["alternatives"][0]["choices"][0], value_id="v:1.2"))
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


# ---------------------------------------------------------------- review fixes


def test_duplicate_requirement_and_alternative_ids_are_schema_errors(graph):
    doc = _sample()
    doc["problem"]["requirements"].append(dict(doc["problem"]["requirements"][0]))
    doc["alternatives"][1]["id"] = doc["alternatives"][0]["id"]
    codes = _codes(_check(doc, graph))
    n = len(doc["problem"]["requirements"]) - 1
    assert ("schema", f"/problem/requirements/{n}/id") in codes
    assert ("schema", "/alternatives/1/id") in codes


def test_explain_without_uncovered_is_a_schema_error(graph):
    doc = _explain()
    del doc["uncovered"]
    assert ("schema", "/uncovered") in _codes(_check(doc, graph))


def test_a_driver_that_is_not_a_string_is_a_schema_error(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["drivers"] = ["Q1", 7]
    assert ("schema", "/alternatives/0/choices/0/drivers/1") in _codes(_check(doc, graph))


def test_a_stance_outside_the_stances_is_a_schema_error(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["evidence"][0]["stance"] = "loves"
    assert ("schema", "/alternatives/0/choices/0/evidence/0/stance") in _codes(_check(doc, graph))
    doc = _own()
    doc["alternatives"][0]["choices"][0]["evidence"] = [{"doc": "s01_p01", "stance": "loves"}]
    assert ("schema", "/alternatives/0/choices/0/evidence/0/stance") in _codes(rationale.check(doc))


def test_a_stance_the_graph_does_not_record_is_a_mismatch(graph):
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["evidence"][0]["stance"] = "rejects"  # the graph: s01_p01 accepts v:1.1
    result = _check(doc, graph)
    problem = next(p for p in result["problems"] if p["code"] == "evidence_stance_mismatch")
    assert problem["path"] == "/alternatives/0/choices/0/evidence/0" and problem["severity"] == "error"
    assert problem["candidates"] == [{"doc": "s01_p01", "stance": "accepts"}]
    assert not result["ok"]


@pytest.mark.parametrize("claim, ok", [("accepts", True), ("rejects", True), ("both", True), ("supports", False)])
def test_a_passage_the_graph_records_as_both_accepts_accepts_or_rejects(graph, claim, ok):
    graph["_by_id"]["v:1.1"]["passages"][0]["stance"] = "both"
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["evidence"][0]["stance"] = claim
    codes = {p["code"] for p in _check(doc, graph)["problems"]}
    assert ("evidence_stance_mismatch" not in codes) is ok


def test_point_returns_unmet_requires_as_data(ws, tmp_path):
    path = _graph_with_requires(ws, tmp_path)
    info = q.point(q.load(path), ["v:1.2"])
    assert info["unmet_requires"] == [{"dimension_id": "d:1", "requires_id": "d:2"}]
    assert any("is not in the point" in w for w in info["warnings"])  # the wording is unchanged
    assert q.point(q.load(path), ["v:1.1", "v:2.1"])["unmet_requires"] == []


def test_the_point_command_only_adds_the_unmet_requires_key(ws, tmp_path):
    path = _graph_with_requires(ws, tmp_path)
    result = _invoke("point", "v:1.2", "--no-llm", "--graph", str(path.parent.parent))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert set(payload) == {"values", "existing", "description", "attested_by", "relations", "warnings",
                            "unmet_requires", "description_source"}
    assert payload["unmet_requires"] == [{"dimension_id": "d:1", "requires_id": "d:2"}]


def test_the_checker_reads_unmet_requires_from_the_data_not_the_wording(ws, tmp_path, monkeypatch):
    path = _graph_with_requires(ws, tmp_path)
    real = q.point
    monkeypatch.setattr(q, "point", lambda g, refs: {**real(g, refs), "warnings": []})
    doc = _sample()
    result = rationale.check(doc, q.load(path), doc["space"]["graph_sha256"])
    assert [(p["code"], p["path"]) for p in result["problems"]] == [("unmet_requires", "/alternatives/1")]
    assert "Replication" in result["problems"][0]["message"]


def test_safe_id_rejects_a_trailing_newline():
    assert rationale.SAFE_ID.fullmatch("toy-store") and not rationale.safe_id("toy-store\n")
    assert not rationale.safe_id("../evil") and not rationale.safe_id("a/b")


# ---------------------------------------------------------------- schema 3: trajectory, budget, rounds, approaches, regions


def test_the_trajectory_steps_are_numbered_in_order_with_earlier_parents(graph):
    doc = _sample()
    doc["trajectory"][1]["step"] = 5
    doc["trajectory"][2]["parent"] = 3
    doc["trajectory"][0]["parent"] = 1
    codes = _codes(_check(doc, graph))
    assert ("bad_step", "/trajectory/1/step") in codes
    assert ("bad_step", "/trajectory/2/parent") in codes  # not an earlier step
    assert ("bad_step", "/trajectory/0/parent") in codes  # the first step has none


def test_moves_and_verdicts_belong_to_the_mode(graph):
    doc = _sample()
    doc["trajectory"][0]["move"] = "region"
    doc["trajectory"][2]["rating"] = "grounded"
    del doc["trajectory"][1]["parent"]
    codes = _codes(_check(doc, graph))
    assert ("bad_step", "/trajectory/0/move") in codes
    assert ("schema", "/trajectory/2/rating") in codes
    assert ("bad_step", "/trajectory/1/parent") in codes  # an exploit step names the step it refines


def test_an_alternative_is_a_step_of_its_approach_with_the_same_values(graph):
    doc = _sample()
    doc["alternatives"][1]["step"] = 2           # a weak step of approach A
    assert ("step_mismatch", "/alternatives/1/step") in _codes(_check(doc, graph))
    doc = _sample()
    doc["trajectory"][0]["values"] = ["v:1.1"]  # step 1 no longer the point A1 takes
    result = _check(doc, graph)
    assert ("step_mismatch", "/alternatives/0/step") in _codes(result)
    doc = _sample()
    doc["alternatives"][0]["step"] = 9
    assert ("step_mismatch", "/alternatives/0/step") in _codes(_check(doc, graph))


def test_step_values_get_the_value_rules(graph):
    doc = _sample()
    doc["trajectory"][0]["values"] = ["1.1", "v:9.9", "v:1.2"]
    codes = _codes(_check(doc, graph))
    assert ("not_canonical", "/trajectory/0/values/0") in codes
    assert ("unknown_id", "/trajectory/0/values/1") in codes
    assert ("two_values_one_dimension", "/trajectory/0/values/2") in codes
    doc["trajectory"][0]["values"] = []
    assert ("schema", "/trajectory/0/values") in _codes(_check(doc, graph))


def test_the_budget_caps_the_trajectory_and_the_mode_caps_the_budget(graph):
    doc = _sample()
    doc["budget"]["max_points"] = 2
    assert ("budget", "/trajectory") in _codes(_check(doc, graph))
    doc["budget"]["max_points"] = 21
    assert ("budget", "/budget/max_points") in _codes(_check(doc, graph))
    doc["budget"]["max_points"] = 20
    assert _check(doc, graph)["ok"]
    ex = _explain()
    ex["budget"]["max_points"] = 13
    assert ("budget", "/budget/max_points") in _codes(_check(ex, graph))
    del doc["budget"]
    assert ("schema", "/budget") in _codes(_check(doc, graph))


def test_explain_has_one_solution_step_and_one_to_three_regions(graph):
    doc = _explain()
    doc["trajectory"][1]["move"] = "solution"
    doc["trajectory"][1]["parent"] = None
    assert ("bad_step", "/trajectory") in _codes(_check(doc, graph))
    doc = _explain()
    doc["regions"] = []
    assert ("schema", "/regions") in _codes(_check(doc, graph))
    doc["regions"] = [dict(_explain()["regions"][0], id=f"G{i}") for i in range(4)]
    assert ("schema", "/regions") in _codes(_check(doc, graph))


def test_a_region_is_a_partial_point_of_the_solution_probed_by_its_step(graph):
    doc = _explain()
    doc["regions"][0]["values"] = ["v:1.2"]
    codes = _codes(_check(doc, graph))
    assert ("region_not_in_solution", "/regions/0/values") in codes
    assert ("step_mismatch", "/regions/0/step") in codes  # step 2 probed v:1.1, not v:1.2
    doc = _explain()
    doc["alternatives"][0]["step"] = 2               # the solution is the solution step
    assert ("step_mismatch", "/alternatives/0/step") in _codes(_check(doc, graph))


def test_search_has_no_regions(graph):
    doc = _sample()
    doc["regions"] = _explain()["regions"]
    assert ("schema", "/regions") in _codes(_check(doc, graph))


def test_search_steps_go_up_one_round_at_a_time(graph):
    doc = _sample()
    doc["trajectory"][1]["round"] = 3
    codes = _codes(_check(doc, graph))
    assert ("bad_step", "/trajectory/1/round") in codes
    doc = _sample()
    doc["trajectory"][2]["round"] = 1                 # back to round 1 after round 2
    assert ("bad_step", "/trajectory/2/round") in _codes(_check(doc, graph))
    doc = _sample()
    doc["trajectory"][2].update(move="seed", parent=None)  # a seed in round 2
    assert ("bad_step", "/trajectory/2/round") in _codes(_check(doc, graph))


def test_exploit_and_ablate_stay_in_the_parents_approach(graph):
    doc = _sample()
    doc["trajectory"][1]["approach"] = "B"
    assert ("bad_step", "/trajectory/1/approach") in _codes(_check(doc, graph))
    doc["trajectory"][1]["move"] = "ablate"
    assert ("bad_step", "/trajectory/1/approach") in _codes(_check(doc, graph))
    doc["trajectory"][1]["move"] = "explore"          # a new approach may start from any step
    assert ("bad_step", "/trajectory/1/approach") not in _codes(_check(doc, graph))


def test_steps_name_a_known_approach(graph):
    doc = _sample()
    doc["trajectory"][2]["approach"] = "Z"
    assert ("step_mismatch", "/trajectory/2/approach") in _codes(_check(doc, graph))


def test_search_needs_approaches_and_a_reason_to_drop_one(graph):
    doc = _sample()
    del doc["approaches"]
    assert ("schema", "/approaches") in _codes(_check(doc, graph))
    doc = _sample()
    doc["approaches"][1]["status"] = "dropped"
    codes = _codes(_check(doc, graph))
    assert ("schema", "/approaches/1/dropped_because") in codes
    assert ("step_mismatch", "/alternatives/1/approach") in codes   # A2 comes from a dropped approach
    doc["approaches"][1]["status"] = "paused"
    assert ("schema", "/approaches/1/status") in _codes(_check(doc, graph))


def test_one_alternative_per_approach(graph):
    doc = _sample()
    doc["alternatives"][1]["approach"] = "A"
    codes = _codes(_check(doc, graph))
    assert ("step_mismatch", "/alternatives/1/approach") in codes
    assert ("step_mismatch", "/alternatives/1/step") in codes       # step 3 is approach B


def test_the_assessment_judges_known_requirements(graph):
    doc = _sample()
    doc["trajectory"][0]["assessment"] = {"Q9": "meets", "R1": "great"}
    codes = _codes(_check(doc, graph))
    assert ("unknown_requirement", "/trajectory/0/assessment/Q9") in codes
    assert ("schema", "/trajectory/0/assessment/R1") in codes
    doc["trajectory"][0]["assessment"] = {}
    assert ("schema", "/trajectory/0/assessment") in _codes(_check(doc, graph))
    del doc["trajectory"][0]["hypothesis"]
    assert ("schema", "/trajectory/0/hypothesis") in _codes(_check(doc, graph))


def test_explain_choices_say_whether_they_are_forced(graph):
    doc = _explain()
    del doc["alternatives"][0]["choices"][0]["forced"]
    doc["alternatives"][0]["choices"][1]["forced"] = "yes"
    codes = _codes(_check(doc, graph))
    assert ("schema", "/alternatives/0/choices/0/forced") in codes
    assert ("schema", "/alternatives/0/choices/1/forced") in codes


def test_explain_has_no_approaches(graph):
    doc = _explain()
    doc["approaches"] = _sample()["approaches"]
    assert ("schema", "/approaches") in _codes(_check(doc, graph))



# ---------------------------------------------------------------- schema 4: ADRs


def test_adrs_are_required_and_name_known_requirements(graph):
    doc = _sample()
    del doc["adrs"]
    assert ("schema", "/adrs") in _codes(_check(doc, graph))
    doc = _sample()
    doc["adrs"][0]["drivers"] = ["Q1", "Z9"]
    assert ("unknown_requirement", "/adrs/0/drivers/1") in _codes(_check(doc, graph))


def test_every_alternative_value_is_in_a_chosen_option(graph):
    doc = _sample()
    doc["adrs"][1]["options"][0]["status"] = "discarded"
    del doc["adrs"][1]["options"][0]["in"]
    codes = _codes(_check(doc, graph))
    assert ("not_in_adr", "/alternatives/0/choices/1") in codes   # A1's v:2.1 is in no chosen option
    assert ("schema", "/adrs/1/options") in codes                 # and ADR2 then chooses nothing


def test_a_chosen_option_is_part_of_the_alternatives_it_names(graph):
    doc = _sample()
    doc["adrs"][0]["options"][0]["in"] = ["A1", "A2"]               # A2 does not take v:1.1
    assert ("adr_mismatch", "/adrs/0/options/0/values") in _codes(_check(doc, graph))
    doc["adrs"][0]["options"][0]["in"] = ["A9"]
    assert ("adr_mismatch", "/adrs/0/options/0/in/0") in _codes(_check(doc, graph))
    doc["adrs"][0]["options"][0]["in"] = []
    assert ("schema", "/adrs/0/options/0/in") in _codes(_check(doc, graph))


def test_option_fields_status_step_and_one_value_per_dimension(graph):
    doc = _sample()
    option = doc["adrs"][1]["options"][1]
    option.update(status="maybe", pros=[""], values=["v:2.2", "v:2.3"], step=1)
    option["in"] = ["A1"]
    codes = _codes(_check(doc, graph))
    assert ("schema", "/adrs/1/options/1/status") in codes
    assert ("schema", "/adrs/1/options/1/pros/0") in codes
    assert ("two_values_one_dimension", "/adrs/1/options/1/values/1") in codes
    assert ("step_mismatch", "/adrs/1/options/1/step") in codes    # step 1 did not evaluate v:2.2
    doc = _sample()
    doc["adrs"][1]["options"][1]["in"] = ["A1"]                     # discarded, yet in an alternative
    assert ("schema", "/adrs/1/options/1/in") in _codes(_check(doc, graph))


def test_explain_adrs_choose_the_solutions_option_once(graph):
    doc = _explain()
    doc["adrs"][0]["options"][1].update(status="chosen", **{"in": ["S"]})
    assert ("schema", "/adrs/0/options") in _codes(_check(doc, graph))
    doc = _explain()
    doc["adrs"][1]["options"][0]["in"] = ["A1"]
    assert ("adr_mismatch", "/adrs/1/options/0/in") in _codes(_check(doc, graph))
