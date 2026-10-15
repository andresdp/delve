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
    assert re.search(r"OKF v0.2 check\s+passed", result.output)
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
    assert result.exit_code == 1 and "stale_after" in result.output and "Traceback" not in result.output


def test_bad_saved_core_threshold_is_reported(ws):
    ws.set("wiki.core_min_sources", "many")
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code == 1 and "core_min_sources" in result.output


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
    assert wb.suggest_core(n) == expected


def test_a_combination_sampled_twice_is_described_once(tmp_path):
    same = [{"dimension_id": "1", "value_id": "1.1"}, {"dimension_id": "2", "value_id": "2.1"}]
    points = {"samples": [{"k": 2, "groups": {
        "attested": [{"point_id": "P001", "values": same}],
        "novel": [{"point_id": "P002", "values": list(reversed(same))},
                  {"point_id": "P003", "values": [{"dimension_id": "1", "value_id": "1.2"}]}]}}]}
    assert [p["point_id"] for p in wb.missing_descriptions(tmp_path, points)] == ["P001", "P003"]


def test_run_without_selection_step_reports_its_final_iteration(ws):
    tax = _taxonomy()
    del tax["selected_clusters"]
    final = tax["iterations"][-1]["clusters"]
    assert wb.selected_dims(tax) == final
    from taxonomy_generator.wiki import Inputs, build
    export = build(Inputs(taxonomy=tax, taxonomy_name="toy", run_label="x", corpus=CORPUS, view="selected"))
    assert [p for p in export.pages if p.path.startswith("concepts/")]
    assert len([p for p in export.pages if p.path.startswith("concepts/")]) == len(final)


def _texts_workspace(ws):
    """Two scanned sources with extracted text, for the source-summary tests."""
    (ws.state_dir / "text").mkdir(parents=True)
    ws.sources_csv.write_text("id,file,title,url,source_type,notes\ns1,a.md,Alpha,,,\ns2,b.md,Beta,,,\n")
    for sid in ("s1", "s2"):
        (ws.text_dir / f"{sid}.md").write_text("Some text about replicas.")
    ws.manifest_path.write_text(json.dumps([
        {"id": "s1", "file": "a.md", "format": "md", "title": "Alpha", "words": 400, "sha256": "h1"},
        {"id": "s2", "file": "b.md", "format": "md", "title": "Beta", "words": 400, "sha256": "h2"}]))


def test_failed_summaries_are_reported_and_retried(ws, fake_llm, monkeypatch):
    ws.set("wiki.source_summaries", True)
    ws.set("wiki.design_points", "none")
    _texts_workspace(ws)
    ok = llm_texts.summarize

    async def flaky(model, title, text):
        if title == "Beta":
            raise RuntimeError("rate limited")
        return await ok(model, title, text)

    monkeypatch.setattr(llm_texts, "summarize", flaky)
    first = _invoke("wiki", "build", "--yes")
    assert first.exit_code == 0, first.output
    flat = " ".join(first.output.split())
    assert "1 of 2 source summaries failed" in flat and "rate limited" in flat
    assert "source summaries written" not in flat or "2 source summaries written" not in flat
    assert list(wb.stored_summaries(ws)[0]) == ["s1"]
    assert wb.missing_summaries(ws) == ["s2"]
    monkeypatch.setattr(llm_texts, "summarize", ok)
    calls = fake_llm.calls
    second = _invoke("wiki", "build", "--yes")
    assert second.exit_code == 0 and "failed" not in second.output
    assert fake_llm.calls == calls + 1 and wb.missing_summaries(ws) == []   # only the failed one again


def test_failed_descriptions_are_reported_and_retried(ws, fake_llm, monkeypatch):
    ws.set("wiki.design_points", "describe")
    ok = llm_texts.describe
    bad = {}

    async def flaky(model, point, dims, domain):
        bad.setdefault("id", point["point_id"])
        if point["point_id"] == bad["id"]:
            raise RuntimeError("boom")
        return await ok(model, point, dims, domain)

    monkeypatch.setattr(llm_texts, "describe", flaky)
    first = _invoke("wiki", "build", "--yes")
    assert first.exit_code == 0, first.output
    assert "design-point descriptions failed" in first.output and "boom" in first.output
    run_dir = ws.root / ws.config()["workspace"]["current_run"]
    points = json.loads((run_dir / wb.POINTS_FILE).read_text())
    assert [p["point_id"] for p in wb.missing_descriptions(run_dir, points)] == [bad["id"]]
    monkeypatch.setattr(llm_texts, "describe", ok)
    calls = fake_llm.calls
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    assert fake_llm.calls == calls + 1 and wb.missing_descriptions(run_dir, points) == []


def test_wiki_quotes_come_from_the_run_corpus(ws):
    run_dir = ws.runs_dir / "20261013_100000"
    (run_dir / runs.RUN_CORPUS).write_text(json.dumps(
        [{**p, "content": f"snapshot {p['id']}"} for p in CORPUS.values()]))
    ws.corpus_path.write_text(json.dumps([{**p, "content": "today"} for p in CORPUS.values()]))
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    pages = "\n".join(p.read_text() for p in (ws.root / "wiki").rglob("*.md"))
    assert "snapshot " in pages and "today" not in pages


def test_run_without_a_snapshot_falls_back_to_the_workspace_corpus(ws):
    run_dir = ws.runs_dir / "20261013_100000"
    assert not (run_dir / runs.RUN_CORPUS).exists()
    assert runs.run_corpus_path(ws, run_dir) == ws.corpus_path
    assert _invoke("wiki", "build", "--yes").exit_code == 0
