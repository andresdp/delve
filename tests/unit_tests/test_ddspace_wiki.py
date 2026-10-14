"""ddspace wiki build/check/open: export layout, saved answers, change log, stored LLM extras (fake model)."""

import copy
import json
import re

import pytest
import yaml
from typer.testing import CliRunner

from delvedspace import cli, runs
from delvedspace import wiki_build as wb
from delvedspace.workspace import Workspace
from taxonomy_generator.wiki import llm_texts, okf
from tests.unit_tests.test_wiki_export import CORPUS, _taxonomy

runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


def _add_run(ws, run_id, taxonomy, kind="mine", **meta):
    run_dir = ws.runs_dir / run_id
    run_dir.mkdir(parents=True)
    (run_dir / f"toy_taxonomy_{run_id}.json").write_text(json.dumps(taxonomy))
    runs.save(run_dir, runs.Run(id=run_id, kind=kind, started_at="x", status="ok", **meta))
    ws.set("workspace.current_run", f"runs/{run_id}")
    return run_dir


@pytest.fixture
def ws(tmp_path, monkeypatch):
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes", "--name", "toy").exit_code == 0
    monkeypatch.chdir(root)
    w = Workspace(root)
    w.corpus_path.write_text(json.dumps(list(CORPUS.values())))
    _add_run(w, "20261013_100000", _taxonomy())
    return w


class FakeModel:
    calls = 0


@pytest.fixture
def fake_llm(monkeypatch):
    FakeModel.calls = 0

    async def summarize(model, title, text):
        FakeModel.calls += 1
        return f"Summary of {title}.", len(text.split())

    async def describe(model, point, dims, domain):
        FakeModel.calls += 1
        return f"Description of {point['point_id']}."

    monkeypatch.setattr(llm_texts, "summarize", summarize)
    monkeypatch.setattr(llm_texts, "describe", describe)
    monkeypatch.setattr("taxonomy_generator.utils.load_chat_model", lambda name: FakeModel())
    return FakeModel


def _front(path):
    return yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S).group(1))


def test_build_writes_an_okf_wiki_site_and_query_data(ws):
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code == 0, result.output
    assert (ws.root / "wiki" / "index.md").is_file() and (ws.root / "site" / "index.html").is_file()
    assert (ws.root / "raw" / "graph.json").is_file() and not (ws.root / "html").exists()
    assert okf.check(ws.root / "wiki") == ([], [])
    assert "OKF v0.2 check: passed" in result.output
    saved = ws.config()["wiki"]
    assert saved["quotes"] is True and saved["design_points"] == "sample" and saved["source_summaries"] is False
    assert saved["core_min_sources"] == 2  # 2 sources in the run: a third, but at least 2
    assert _invoke("query", "dims").exit_code == 0


def test_saved_answers_are_reused(ws):
    ws.set("wiki.quotes", False)
    ws.set("wiki.design_points", "none")
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    text = "".join(p.read_text() for p in (ws.root / "wiki").rglob("*.md"))
    assert "Continuity writes a WAL to S3." not in text
    assert not (ws.root / "wiki" / "designs").exists()


def test_log_records_creation_rebuild_and_update_newest_first(ws):
    _invoke("wiki", "build", "--yes")
    _invoke("wiki", "build", "--yes")
    tax = copy.deepcopy(_taxonomy())
    dims = tax["selected_clusters"]
    dims[1]["values"] = [v for v in dims[1]["values"] if v["label"] != "Lower latency"]
    dims[0]["values"].append({"id": "1.4", "label": "Object storage", "status": "accepted", "description": "d.",
                              "supporting_doc_ids": ["s03_p01"]})
    dims[0]["values"][1]["status"] = "accepted"
    _add_run(ws, "20261014_090000", tax, kind="update-test", seed_run="20261013_100000", new_source_ids=["s3"])
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    log = (ws.root / "wiki" / "log.md").read_text()
    update, rebuild, creation = log.index("**Update**"), log.index("**Rebuild**"), log.index("**Creation**")
    assert update < rebuild < creation and log.count("## ") == 1   # same day: one heading, newest entry first
    assert "New sources: s3" in log and "Values added (1): Object storage (Source of truth)" in log
    assert "Values removed (1): Lower latency (Replication)" in log
    assert "WAL in S3 (Source of truth): mixed → accepted" in log
    assert okf.check(ws.root / "wiki")[0] == []


def test_append_log_puts_a_new_day_on_top(tmp_path):
    path = tmp_path / "log.md"
    wb.append_log(path, "- old", day="2026-10-12")
    wb.append_log(path, "- new", day="2026-10-14")
    text = path.read_text()
    assert text.index("2026-10-14") < text.index("2026-10-12")
    assert okf._check_log("log.md", text) == []


def test_describe_and_summaries_are_stored_and_reused(ws, fake_llm):
    ws.set("wiki.design_points", "describe")
    ws.set("wiki.source_summaries", True)
    ws.set("wiki.core_min_sources", 2)
    (ws.state_dir / "text").mkdir(parents=True)
    ws.sources_csv.write_text("id,file,title,url,source_type,notes\ns1,a.md,Alpha,,,\ns2,b.md,Beta,,,\n")
    from delvedspace import sources as src
    for sid in ("s1", "s2"):
        (ws.text_dir / f"{sid}.md").write_text("Some text about replicas.")
    ws.manifest_path.write_text(json.dumps([
        {"id": "s1", "file": "a.md", "format": "md", "title": "Alpha", "words": 400, "sha256": "h1"},
        {"id": "s2", "file": "b.md", "format": "md", "title": "Beta", "words": 400, "sha256": "h2"}]))
    assert len(src.load_manifest(ws)) == 2
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code == 0, result.output
    first = fake_llm.calls
    run_dir = ws.root / ws.config()["workspace"]["current_run"]
    points = wb.all_points(json.loads((run_dir / wb.POINTS_FILE).read_text()))
    assert first == len(points) + 2 and points
    assert json.loads((run_dir / wb.DESCRIPTIONS_FILE).read_text())["descriptions"]
    assert "Summary of Alpha." in (ws.root / "wiki" / "sources" / "s1.md").read_text()
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    assert fake_llm.calls == first                      # nothing new to write
    manifest = json.loads(ws.manifest_path.read_text())
    manifest[0]["sha256"] = "changed"
    ws.manifest_path.write_text(json.dumps(manifest))
    _invoke("wiki", "build", "--yes")
    assert fake_llm.calls == first + 1                  # only the changed source again


def test_no_llm_uses_only_stored_texts(ws, fake_llm):
    ws.set("wiki.design_points", "describe")
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    assert fake_llm.calls == 0


def test_design_points_leave_out_the_control_group(ws):
    _invoke("wiki", "build", "--yes")
    run_dir = ws.root / ws.config()["workspace"]["current_run"]
    data = json.loads((run_dir / wb.POINTS_FILE).read_text())
    assert all(not s["groups"]["control"] for s in data["samples"]) and data["attest_by"] == "source"


def test_interactive_build_asks_and_saves(ws, monkeypatch):
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    answers = "\n".join(["n", "n", "none", "2"]) + "\n"    # quotes, summaries, design points, core threshold
    result = _invoke("wiki", "build", input=answers)
    assert result.exit_code == 0, result.output
    saved = ws.config()["wiki"]
    assert saved["quotes"] is False and saved["design_points"] == "none" and saved["core_min_sources"] == 2
    again = _invoke("wiki", "build")                        # answers saved: no questions this time
    assert again.exit_code == 0 and "A few questions" not in again.output


def test_stale_after_marks_pages(ws, monkeypatch):
    ws.set("wiki.stale_after", "90d")
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    fm = _front(ws.root / "wiki" / "concepts" / "source-of-truth.md")
    assert re.match(r"\d{4}-\d{2}-\d{2}T", fm["stale_after"])


def test_bad_refresh_period_is_reported(ws):
    ws.set("wiki.stale_after", "soon")
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code != 0


def test_build_needs_a_run(tmp_path, monkeypatch):
    root = tmp_path / "empty"
    _invoke("init", str(root), "--yes")
    monkeypatch.chdir(root)
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code == 1 and "ddspace mine" in result.output


def test_selection_dropping_everything_is_explained(ws):
    tax = _taxonomy()
    tax["selected_clusters"] = []
    _add_run(ws, "20261014_120000", tax)
    result = _invoke("wiki", "build", "--yes")
    assert "dropped all" in result.output and "min_dimension_sources" in result.output


def test_check_and_open(ws):
    _invoke("wiki", "build", "--yes")
    assert _invoke("wiki", "check").exit_code == 0
    (ws.root / "wiki" / "concepts" / "broken.md").write_text("no frontmatter\n")
    result = _invoke("wiki", "check")
    assert result.exit_code == 1 and "broken.md" in result.output
    printed = _invoke("wiki", "open", "--print")
    assert printed.exit_code == 0 and printed.output.strip().endswith("site/index.html")


@pytest.mark.parametrize("n, expected", [(1, 1), (2, 2), (5, 2), (9, 3), (30, 10)])
def test_suggested_core_threshold(n, expected):
    assert wb.suggest_core([], n) == expected
