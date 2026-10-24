"""ddspace import: a mined run or an external decision model becomes the workspace's current run."""

import csv
import json

import pytest
from typer.testing import CliRunner

from delvedspace import cli, importer, runs
from delvedspace.workspace import Workspace, read_json
from tests.unit_tests.test_wiki_export import CORPUS, _taxonomy

runner = CliRunner()


def _invoke(*args):
    return runner.invoke(cli.app, list(args))


@pytest.fixture
def ws(tmp_path, monkeypatch):
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes", "--name", "toy").exit_code == 0
    monkeypatch.chdir(root)
    return Workspace(root)


@pytest.fixture
def run_files(tmp_path):
    folder = tmp_path / "inputs"
    folder.mkdir()
    taxonomy = folder / "toy_taxonomy_20261016_000000.json"
    taxonomy.write_text(json.dumps(_taxonomy()))
    corpus = folder / "toy_corpus.json"
    corpus.write_text(json.dumps(list(CORPUS.values())))
    sources = folder / "sources.csv"
    with sources.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "url"])
        w.writerow(["s1", "First source", "https://example.org/1"])
        w.writerow(["s2", "Second source", "https://example.org/2"])
    return taxonomy, corpus, sources


def _model():
    return {
        "decisions": [
            {"id": "store_decision", "name": "Data storage", "question": "Where is the data stored?", "description": ""},
            {"id": "access_decision", "name": "Data access", "question": "How is the data accessed?",
             "description": "How consumers reach the data."},
        ],
        "options": [
            {"id": "lake", "name": "Data lake", "decision_ids": ["store_decision"], "description": "Raw files."},
            {"id": "warehouse", "name": "Data warehouse", "decision_ids": ["store_decision"], "description": ""},
            {"id": "layer", "name": "Abstraction layer", "decision_ids": ["access_decision", "store_decision"],
             "description": "An access layer."},
            {"id": "direct", "name": "Direct access", "decision_ids": ["access_decision"], "description": ""},
            {"id": "orphan", "name": "Orphan option", "decision_ids": [], "description": "", "unattached": True},
        ],
        "decision_links": [{"from": "store_decision", "to": "access_decision",
                            "stereotypes": ["Consider If Not Decided Yet"], "label": "offer an abstraction layer"}],
        "forces": [{"id": "maintainability", "name": "Maintainability"}],
        "impacts": [{"option_id": "lake", "force_id": "maintainability", "impact": "+"}],
    }


# ---------------------------------------------------------------- U1: runs


def test_import_run_makes_it_current_and_buildable(ws, run_files):
    taxonomy, corpus, sources = run_files
    result = _invoke("import", str(taxonomy), "--kind", "run", "--corpus", str(corpus), "--sources", str(sources),
                     "--yes")
    assert result.exit_code == 0, result.output
    run_dir = runs.current_run_dir(ws)
    assert runs.find_taxonomy(run_dir) is not None
    run = runs.load(run_dir)
    assert run.kind == "import-run" and run.status == "ok" and run.source_ids == ["s1", "s2"]
    assert (run_dir / runs.RUN_CORPUS).is_file() and ws.sources_csv.is_file()
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    assert (ws.root / "raw" / "graph.json").is_file()


def test_imported_run_answers_queries_and_points(ws, run_files):
    taxonomy, corpus, sources = run_files
    assert _invoke("import", str(taxonomy), "--kind", "run", "--corpus", str(corpus), "--sources", str(sources),
                   "--yes").exit_code == 0
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    dims = json.loads(_invoke("query", "dims").output)
    assert {d["label"] for d in dims} >= {"Source of truth", "Replication"}
    point = json.loads(_invoke("point", "Disk quorum", "Three-phase commit", "--no-llm").output)
    assert [s["id"] for s in point["attested_by"]] == ["s:s1"]


def test_import_run_without_corpus_has_no_quotes(ws, run_files):
    taxonomy, _, sources = run_files
    assert _invoke("import", str(taxonomy), "--kind", "run", "--sources", str(sources), "--yes").exit_code == 0
    assert not (runs.current_run_dir(ws) / runs.RUN_CORPUS).exists()
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    page = next((ws.root / "wiki" / "entities").glob("disk-quorum*.md")).read_text()
    assert "Spokes keeps" not in page


def test_missing_input_fails_and_keeps_the_current_run(ws, run_files):
    taxonomy, _, _ = run_files
    assert _invoke("import", str(taxonomy), "--kind", "run", "--yes").exit_code == 0
    before = ws.config()["workspace"]["current_run"]
    result = _invoke("import", str(taxonomy.parent / "missing.json"), "--kind", "run", "--yes")
    assert result.exit_code != 0 and "missing.json" in result.output
    assert ws.config()["workspace"]["current_run"] == before


def test_replacing_a_current_run_needs_yes(ws, run_files):
    taxonomy, _, _ = run_files
    assert _invoke("import", str(taxonomy), "--kind", "run", "--yes").exit_code == 0
    before = ws.config()["workspace"]["current_run"]
    result = _invoke("import", str(taxonomy), "--kind", "run")
    assert result.exit_code != 0 and "--yes" in result.output
    assert ws.config()["workspace"]["current_run"] == before


# ---------------------------------------------------------------- U2: decision models


def _dims(taxonomy):
    return {d["name"]: d for d in taxonomy["selected_clusters"]}


def test_model_maps_decisions_options_and_links():
    taxonomy = importer.model_to_taxonomy(_model(), name="toy-model")
    dims = _dims(taxonomy)
    assert set(dims) == {"Data storage", "Data access"}
    assert [v["label"] for v in dims["Data storage"]["values"]] == ["Data lake", "Data warehouse", "Abstraction layer"]
    assert [v["label"] for v in dims["Data access"]["values"]] == ["Abstraction layer", "Direct access"]
    relations = dims["Data storage"]["relations"]
    assert len(relations) == 1 and relations[0]["type"] == "affects"
    assert relations[0]["target_id"] == dims["Data access"]["id"]
    assert not dims["Data access"]["relations"]


def test_model_gives_unique_value_ids_and_skips_unattached_options():
    taxonomy = importer.model_to_taxonomy(_model(), name="toy-model")
    values = [v for d in taxonomy["selected_clusters"] for v in d["values"]]
    assert len({v["id"] for v in values}) == len(values) == 5
    assert "Orphan option" not in {v["label"] for v in values}
    assert all(v["status"] == "accepted" and v["supporting_doc_ids"] == [] for v in values)


def test_model_uses_the_question_when_a_decision_has_no_description():
    dims = _dims(importer.model_to_taxonomy(_model(), name="toy-model"))
    assert dims["Data storage"]["description"] == "Where is the data stored?"
    assert dims["Data access"]["description"] == "How consumers reach the data."


def test_model_leaves_out_forces_and_impacts():
    text = json.dumps(importer.model_to_taxonomy(_model(), name="toy-model"))
    assert "maintainability" not in text.lower() and "impact" not in text


def test_opposite_links_are_normalized():
    model = _model()
    model["decision_links"].append({"from": "access_decision", "to": "store_decision",
                                    "stereotypes": ["Consider If Not Decided Yet"], "label": "back link"})
    taxonomy = importer.model_to_taxonomy(model, name="toy-model")
    pairs = [frozenset((d["id"], r["target_id"])) for d in taxonomy["selected_clusters"] for r in d["relations"]]
    assert len(pairs) == len(set(pairs)) == 1


def test_import_model_builds_an_expert_wiki(ws, tmp_path):
    path = tmp_path / "gt_model.json"
    path.write_text(json.dumps(_model()))
    result = _invoke("import", str(path), "--kind", "decision-model", "--yes")
    assert result.exit_code == 0, result.output
    run_dir = runs.current_run_dir(ws)
    assert runs.load(run_dir).kind == "import-model"
    saved = ws.config()["wiki"]
    assert saved["quotes"] is False and saved["design_points"] == "none" and saved["core_min_sources"] == 0
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    graph = read_json(ws.root / "raw" / "graph.json")
    assert not [n for n in graph["nodes"] if n["id"].startswith("s:")]
    dims = json.loads(_invoke("query", "dims").output)
    assert len(dims) == 2 and all(d["core"] for d in dims)
    point = json.loads(_invoke("point", "Data lake", "Direct access", "--no-llm").output)
    assert point["attested_by"] == []
