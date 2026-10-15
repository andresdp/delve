"""ddspace check (configuration, missing items, phase progress) and ddspace reset --all / --purge."""

import json

import pytest
from typer.testing import CliRunner

from delvedspace import check as chk
from delvedspace import cli
from delvedspace import sources as src
from delvedspace.workspace import Workspace
from tests.unit_tests.test_ddspace_wiki import _add_run
from tests.unit_tests.test_wiki_export import CORPUS, _taxonomy

runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


def _para(n, word="replica"):
    return " ".join([word] * (n - 1) + [word + "."])


@pytest.fixture
def ws(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes", "--name", "toy").exit_code == 0
    monkeypatch.chdir(root)
    return Workspace(root)


def _states(ws):
    report = chk.check(ws)
    return {i.name: i.state for i in report.config + report.phases}, report


def test_fresh_workspace_points_at_the_missing_key_and_the_sources(ws):
    states, report = _states(ws)
    assert states["OPENAI_API_KEY"] == "pending" and states["Sources"] == "pending"
    assert states["Design space (mine)"] == "pending" and states["Wiki"] == "pending"
    assert [i.name for i in report.next_steps] == ["OPENAI_API_KEY", "Sources"]


def test_phases_progress_and_go_stale(ws, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-SECRET")
    (ws.sources_dir / "a.md").write_text("# A\n\n" + _para(400))
    states, _ = _states(ws)
    assert states["Sources"] == "pending"                       # files, not scanned yet
    _invoke("sources")
    states, report = _states(ws)
    assert states["Sources"] == "done" and states["Corpus"] == "done"
    assert report.next_steps[0].next == "ddspace mine"
    (ws.sources_dir / "b.md").write_text("# B\n\n" + _para(400, "quorum"))
    states, _ = _states(ws)
    assert states["Sources"] == "stale"                         # a new file since the scan
    (ws.sources_dir / "a.md").write_text("# A\n\n" + _para(380))
    src.scan(ws)
    states, _ = _states(ws)
    assert states["Corpus"] == "stale"                          # scanned, but the corpus is older


def test_mined_and_built_workspace_and_a_stale_wiki(ws, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-SECRET")
    ws.corpus_path.write_text(json.dumps(list(CORPUS.values())))
    _add_run(ws, "20261013_100000", _taxonomy())
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    states, _ = _states(ws)
    assert states["Design space (mine)"] == "done" and states["Wiki"] == "done"
    assert states["Agent setup"] == "pending"
    _invoke("agent", "setup", "--yes")
    assert _states(ws)[0]["Agent setup"] == "done"
    _add_run(ws, "20261014_090000", _taxonomy())                # a newer run, wiki not rebuilt
    states, report = _states(ws)
    assert states["Wiki"] == "stale" and states["Agent setup"] == "done"   # AGENTS.md matches the built wiki
    assert "ddspace wiki build" in [i.next for i in report.next_steps]
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    states, report = _states(ws)
    assert states["Wiki"] == "done" and states["Agent setup"] == "stale"
    assert [i.next for i in report.next_steps] == ["ddspace agent setup"]


def test_a_failed_run_after_the_current_one_is_reported(ws, monkeypatch):
    from delvedspace import runs
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-SECRET")
    _add_run(ws, "20261013_100000", _taxonomy())
    failed = ws.runs_dir / "20261014_100000"
    failed.mkdir()
    runs.save(failed, runs.Run(id=failed.name, kind="mine", started_at="x", status="failed"))
    states, report = _states(ws)
    assert states["Last run"] == "failed"
    assert any(i.name == "Last run" and runs.LOG_FILE in i.detail for i in report.phases)


def test_check_command_masks_the_key_and_prints_json(ws, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-SECRETSECRET")
    result = _invoke("check")
    assert result.exit_code == 0 and "SECRETSECRET" not in result.output and "Pipeline" in result.output
    data = json.loads(_invoke("check", "--json").output)
    assert data["next"] == ["copy files into the sources folder, then: ddspace sources"]
    assert {p["name"] for p in data["phases"]} >= {"Sources", "Corpus", "Wiki", "Chat index (ask)"}


def test_bad_embedding_setting_is_a_configuration_failure(ws):
    text = ws.config_path.read_text().replace('embedding: "openai/text-embedding-3-small"',
                                              'embedding: "anthropic/x"')
    ws.config_path.write_text(text)
    states, report = _states(ws)
    assert states["Embedding model"] == "failed" and report.next_steps[0].name == "Embedding model"


# ---------------------------------------------------------------- reset --all / --purge


@pytest.fixture
def built(ws, monkeypatch):
    (ws.sources_dir / "a.md").write_text("# A\n\n" + _para(400))
    _invoke("sources")
    ws.state_dir.mkdir(exist_ok=True)
    (ws.state_dir / "source_summaries.json").write_text("{}")
    _add_run(ws, "20261013_100000", _taxonomy())
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    return ws


def test_reset_all_archives_what_was_built_from_the_sources(built):
    ws = built
    result = _invoke("reset", "--all", "--yes")
    assert result.exit_code == 0, result.output
    [archive] = list((ws.state_dir / "archive").iterdir())
    assert (archive / "corpus.json").is_file() and (archive / ".ddspace" / "text").is_dir()
    assert (archive / ".ddspace" / "source_summaries.json").is_file() and (archive / "runs").is_dir()
    assert not ws.corpus_path.exists() and not (ws.state_dir / "text").exists()
    assert (ws.sources_dir / "a.md").is_file() and ws.sources_csv.is_file() and ws.config_path.is_file()
    assert "ddspace sources" in result.output
    states, _ = _states(ws)
    assert states["Sources"] == "pending" and states["Corpus"] == "pending"


def test_reset_purge_deletes_instead_of_archiving(built):
    ws = built
    result = _invoke("reset", "--all", "--purge", "--yes")
    assert result.exit_code == 0, result.output
    assert not (ws.state_dir / "archive").exists() and not ws.corpus_path.exists()
    assert not (ws.root / "site").exists() and (ws.sources_dir / "a.md").is_file()
    assert "deleted" in (ws.root / "wiki" / "log.md").read_text()


def test_reset_rejects_wiki_only_with_all(built):
    assert _invoke("reset", "--all", "--wiki-only", "--yes").exit_code == 1


def test_purge_asks_before_deleting(built, monkeypatch):
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    result = _invoke("reset", "--purge", input="n\n")
    assert result.exit_code == 0 and "Delete for good?" in result.output and (built.root / "site").exists()
