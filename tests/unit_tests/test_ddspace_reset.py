"""ddspace reset: archives runs and wiki (or only the wiki), keeps sources, settings and caches."""

import json

import pytest
from typer.testing import CliRunner

from delvedspace import cli
from delvedspace.workspace import Workspace
from tests.unit_tests.test_ddspace_wiki import _add_run
from tests.unit_tests.test_wiki_export import CORPUS, _taxonomy

runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    root = tmp_path / "space"
    _invoke("init", str(root), "--yes", "--name", "toy")
    monkeypatch.chdir(root)
    w = Workspace(root)
    w.corpus_path.write_text(json.dumps(list(CORPUS.values())))
    (w.sources_dir / "a.md").write_text("text")
    w.state_dir.mkdir(exist_ok=True)
    (w.state_dir / "source_summaries.json").write_text("{}")
    (w.root / "AGENTS.md").write_text("guide")
    (w.root / ".env").write_text("OPENAI_API_KEY=x\n")
    _add_run(w, "20261013_100000", _taxonomy())
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    return w


def _archives(ws):
    return list((ws.state_dir / "archive").iterdir())


def test_reset_archives_runs_and_wiki_and_keeps_the_rest(ws):
    result = _invoke("reset", "--yes")
    assert result.exit_code == 0, result.output
    [archive] = _archives(ws)
    assert {p.name for p in archive.iterdir()} == {"runs", "wiki", "site", "raw"}
    assert not list(ws.runs_dir.iterdir()) and not (ws.root / "site").exists()
    for kept in ("sources/a.md", "corpus.json", "ddspace.yaml", ".env", "AGENTS.md", ".ddspace/source_summaries.json"):
        assert (ws.root / kept).exists(), kept
    assert ws.config()["workspace"]["current_run"] is None
    assert "**Reset**" in (ws.root / "wiki" / "log.md").read_text()


def test_mine_starts_from_scratch_after_a_reset(ws, monkeypatch):
    from delvedspace import runs
    from tests.unit_tests.test_ddspace_runs import FakePipeline
    fake = FakePipeline()
    monkeypatch.setattr(runs, "run_pipeline", fake)
    assert _invoke("mine", "--yes").exit_code == 1          # a design space exists
    _invoke("reset", "--yes")
    assert _invoke("mine", "--yes").exit_code == 0 and "--taxonomy" not in fake.calls[-1]


def test_after_reset_the_next_build_logs_above_the_reset(ws):
    _invoke("reset", "--wiki-only", "--yes")
    assert ws.config()["workspace"]["current_run"] == "runs/20261013_100000"
    assert (ws.runs_dir / "20261013_100000").is_dir()
    assert _invoke("wiki", "build", "--yes").exit_code == 0
    log = (ws.root / "wiki" / "log.md").read_text()
    assert log.index("**Creation**") < log.index("**Reset**")
    assert _invoke("wiki", "check").exit_code == 0


def test_declining_touches_nothing(ws, monkeypatch):
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    result = _invoke("reset", input="n\n")
    assert result.exit_code == 0 and not (ws.state_dir / "archive").exists()
    assert (ws.root / "site" / "index.html").is_file()


def test_without_a_terminal_reset_needs_yes(ws):
    result = _invoke("reset")
    assert result.exit_code == 1 and "--yes" in result.output and not (ws.state_dir / "archive").exists()


def test_nothing_to_reset(tmp_path, monkeypatch):
    root = tmp_path / "empty"
    _invoke("init", str(root), "--yes")
    monkeypatch.chdir(root)
    result = _invoke("reset", "--yes")
    assert result.exit_code == 0 and "Nothing to reset" in result.output
