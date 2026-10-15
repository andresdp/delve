"""ddspace mine and update: argument mapping to the pipeline, run folders and the current-run pointer.

The pipeline is replaced by a fake that writes a taxonomy JSON, so no LLM is called.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from delvedspace import cli, runs
from delvedspace import sources as src
from delvedspace.workspace import Workspace

runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


def _para(n: int, word: str = "replica") -> str:
    return " ".join([word] * (n - 1) + [word + "."])


class FakePipeline:
    """Stands in for ``runs.run_pipeline``: records each call and writes a taxonomy JSON into --output."""

    OUTPUT = ["2026-10-14 10:00:00 [INFO] __main__: Loading corpus from file: corpus.json",
              "🔬 Open coding minibatch 1", "🔄 Updating taxonomy", "Traceback-like noise line"]

    def __init__(self, code=0, metrics=None):
        self.calls, self.code, self.metrics, self.logged = [], code, metrics, []

    def __call__(self, ws, argv, log_path=None, on_line=None):
        self.calls.append(argv)
        self.logged.append(log_path)
        if log_path is not None:
            with open(log_path, "a") as log:
                for line in self.OUTPUT:
                    log.write(line + "\n")
                    if on_line:
                        on_line(line)
        if self.code == 0 and "--html-report" not in argv:
            out = ws.root / argv[argv.index("--output") + 1]
            data = {"iterations": [{"clusters": [{"id": "1", "name": "Replication", "values": [{}, {}]}]}],
                    "selected_clusters": [{"id": "1", "name": "Replication", "values": [{}, {}]}]}
            if self.metrics:
                data["run_metrics"] = self.metrics
            (out / f"space_taxonomy_{len(self.calls):04d}.json").write_text(json.dumps(data))
        return self.code


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A workspace with two scanned sources and a corpus; the current folder is its root."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    monkeypatch.chdir(root)
    w = Workspace(root)
    (w.sources_dir / "a.md").write_text("# A\n\n" + _para(400))
    (w.sources_dir / "b.md").write_text("# B\n\n" + _para(400, "quorum"))
    src.scan(w)
    src.build_corpus(w)
    return w


@pytest.fixture
def fake(monkeypatch):
    f = FakePipeline(metrics={"total_tokens": 100_000, "elapsed_seconds": 120})
    monkeypatch.setattr(runs, "run_pipeline", f)
    return f


def _current(ws):
    return ws.config()["workspace"]["current_run"]


def test_mine_runs_the_pipeline_in_a_new_run_folder_and_makes_it_current(ws, fake):
    result = _invoke("mine", "--yes", "--max-dimensions", "4")
    assert result.exit_code == 0, result.output
    argv = fake.calls[0]
    run_dir = ws.root / argv[argv.index("--output") + 1]
    assert argv[:4] == ["--corpus", "corpus.json", "--config", "ddspace.yaml"]
    assert argv[argv.index("-k") + 1] == "4"
    assert run_dir.parent == ws.runs_dir and _current(ws) == f"runs/{run_dir.name}"
    run = runs.load(run_dir)
    assert run.kind == "mine" and run.status == "ok" and run.source_ids == ["s1", "s2"]
    assert run.passages == len(json.loads(ws.corpus_path.read_text())) and run.taxonomy
    assert "1 dimensions, 2 values" in result.output


def test_mine_refuses_to_replace_a_design_space_unless_fresh(ws, fake):
    assert _invoke("mine", "--yes").exit_code == 0
    first = _current(ws)
    result = _invoke("mine", "--yes")
    assert result.exit_code == 1 and "ddspace update" in result.output and "--fresh" in result.output
    assert _invoke("mine", "--yes", "--fresh").exit_code == 0
    assert _current(ws) != first and "--taxonomy" not in fake.calls[-1]


def test_a_failed_run_keeps_the_current_design_space(ws, fake, monkeypatch):
    assert _invoke("mine", "--yes").exit_code == 0
    first = _current(ws)
    monkeypatch.setattr(runs, "run_pipeline", FakePipeline(code=1))
    result = _invoke("mine", "--yes", "--fresh")
    assert result.exit_code == 1 and "unchanged" in result.output
    assert _current(ws) == first
    failed = [runs.load(d) for d in ws.runs_dir.iterdir() if runs.load(d).status == "failed"]
    assert len(failed) == 1 and failed[0].finished_at


def test_mine_needs_a_corpus(ws, fake):
    ws.corpus_path.unlink()
    result = _invoke("mine", "--yes")
    assert result.exit_code == 1 and "ddspace corpus" in result.output and not fake.calls


def test_declining_the_confirmation_starts_nothing(ws, fake, monkeypatch):
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    result = _invoke("mine", input="n\n")
    assert result.exit_code == 0 and not fake.calls and not list(ws.runs_dir.iterdir())
    assert "Estimate (rough, from the C3 sample)" in result.output


def test_update_feedback_seeds_from_the_current_run(ws, fake, tmp_path):
    _invoke("mine", "--yes")
    seed_run = Path(_current(ws)).name
    seed = runs.current_taxonomy(ws)
    note = tmp_path / "feedback.md"
    note.write_text("Merge the two replication dimensions.\n")
    result = _invoke("update", "--feedback-file", str(note), "--yes")
    assert result.exit_code == 0, result.output
    argv = fake.calls[-1]
    assert argv[argv.index("--taxonomy") + 1] == runs.relative(ws, seed)
    assert argv[argv.index("--feedback") + 1] == "Merge the two replication dimensions."
    assert "--mode" not in argv
    run = runs.load(ws.root / _current(ws))
    assert run.kind == "update-feedback" and run.seed_run == seed_run and run.feedback.startswith("Merge")


@pytest.mark.parametrize("args, message", [
    ([], "Choose one"),
    (["--test", "--feedback", "x"], "Choose one"),
    (["--feedback", "x", "--feedback-file", "f.md"], "either"),
    (["--feedback", "x", "--sources", "a.md"], "--sources goes with --test"),
])
def test_update_rejects_unclear_requests(ws, fake, args, message):
    _invoke("mine", "--yes")
    result = _invoke("update", *args, "--yes")
    assert result.exit_code == 1 and message in result.output


def test_update_needs_a_design_space(ws, fake):
    result = _invoke("update", "--feedback", "x", "--yes")
    assert result.exit_code == 1 and "ddspace mine" in result.output


def test_update_test_adds_new_sources_and_classifies_only_their_passages(ws, fake, tmp_path):
    _invoke("mine", "--yes")
    seed = runs.current_taxonomy(ws)
    before = json.loads(ws.corpus_path.read_text())
    new_file = tmp_path / "c.md"
    new_file.write_text("# C\n\n" + _para(400, "sharding"))
    result = _invoke("update", "--test", "--sources", str(new_file), "--yes")
    assert result.exit_code == 0, result.output
    assert (ws.sources_dir / "c.md").is_file()
    after = json.loads(ws.corpus_path.read_text())
    assert after[:len(before)] == before and {p["source_id"] for p in after[len(before):]} == {"s3"}
    argv = fake.calls[-1]
    assert argv[argv.index("--mode") + 1] == "test"
    assert argv[argv.index("--taxonomy") + 1] == runs.relative(ws, seed)
    run_dir = ws.root / _current(ws)
    used = json.loads((ws.root / argv[argv.index("--corpus") + 1]).read_text())
    assert {p["source_id"] for p in used} == {"s3"} and (run_dir / "corpus_new.json").is_file()
    run = runs.load(run_dir)
    assert run.kind == "update-test" and run.new_source_ids == ["s3"] and run.source_ids == ["s1", "s2", "s3"]


def test_update_test_without_new_sources_explains(ws, fake):
    _invoke("mine", "--yes")
    result = _invoke("update", "--test", "--yes")
    assert result.exit_code == 1 and "No new sources" in result.output


def test_update_test_picks_up_files_dropped_into_the_sources_folder(ws, fake):
    _invoke("mine", "--yes")
    (ws.sources_dir / "d.md").write_text("# D\n\n" + _para(400, "caching"))
    assert _invoke("update", "--test", "--yes").exit_code == 0
    assert runs.load(ws.root / _current(ws)).new_source_ids == ["s3"]


def test_html_report_is_written_only_on_request(ws, fake):
    _invoke("mine", "--yes")
    assert not any("--html-report" in c for c in fake.calls)
    _invoke("mine", "--yes", "--fresh", "--html-report")
    html = fake.calls[-1]
    assert html[0] == "--html-report" and html[1] == runs.relative(ws, runs.current_taxonomy(ws))


def test_estimate_scales_from_the_last_successful_run(ws, fake):
    assert runs.estimate(ws, 10, 10).basis.startswith("rough")
    _invoke("mine", "--yes")
    passages = runs.load(ws.root / _current(ws)).passages
    est = runs.estimate(ws, passages * 2, 10)
    assert est.basis.startswith("scaled") and est.tokens == 200_000 and est.seconds == 240


def test_pipeline_command_runs_the_installed_pipeline(ws):
    assert runs.run_pipeline(ws, ["--help"]) == 0


def test_a_run_keeps_the_corpus_it_covers(ws, fake):
    covered = json.loads(ws.corpus_path.read_text())
    assert _invoke("mine", "--yes").exit_code == 0
    run_dir = ws.root / _current(ws)
    assert json.loads((run_dir / runs.RUN_CORPUS).read_text()) == covered
    ws.corpus_path.write_text("[]")
    assert json.loads((run_dir / runs.RUN_CORPUS).read_text()) == covered
    assert "runs/*/corpus*.json" in (ws.root / ".gitignore").read_text()


def test_a_failed_run_keeps_no_corpus_snapshot(ws, monkeypatch):
    monkeypatch.setattr(runs, "run_pipeline", FakePipeline(code=1))
    assert _invoke("mine", "--yes").exit_code == 1
    assert not list(ws.runs_dir.glob(f"*/{runs.RUN_CORPUS}"))


def test_mine_is_compact_by_default_and_logs_the_full_output(ws, fake):
    result = _invoke("mine", "--yes")
    assert result.exit_code == 0, result.output
    run_dir = ws.root / _current(ws)
    log = (run_dir / runs.LOG_FILE).read_text()
    assert fake.logged[0] == run_dir / runs.LOG_FILE and "Open coding minibatch 1" in log
    assert "Traceback-like noise line" not in result.output and "pipeline.log" in result.output


def test_verbose_shows_the_pipeline_output(ws, fake):
    assert _invoke("mine", "--yes", "--verbose").exit_code == 0
    assert fake.logged == [None]


def test_a_failed_compact_run_shows_the_end_of_its_log(ws, monkeypatch):
    monkeypatch.setattr(runs, "run_pipeline", FakePipeline(code=1))
    result = _invoke("mine", "--yes")
    assert result.exit_code == 1 and "Traceback-like noise line" in result.output and "pipeline.log" in result.output


def test_logged_pipeline_run_streams_lines(ws, tmp_path):
    seen = []
    log = tmp_path / "pipeline.log"
    assert runs.run_pipeline(ws, ["--help"], log_path=log, on_line=seen.append) == 0
    assert any("--corpus" in line for line in seen) and "--corpus" in log.read_text()


def test_estimate_ignores_test_mode_runs(ws, fake, tmp_path):
    _invoke("mine", "--yes")
    new_file = tmp_path / "c.md"
    new_file.write_text("# C\n\n" + _para(400, "sharding"))
    _invoke("update", "--test", "--sources", str(new_file), "--yes")
    assert runs.estimate(ws, 10, 10).basis.endswith(runs.load(ws.root / _current(ws)).seed_run)


def test_small_estimates_are_shown_in_thousands(ws, fake, monkeypatch):
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    result = _invoke("mine", input="n\n")
    assert "M tokens" in result.output or "k tokens" in result.output
    assert "0.0M" not in cli._format_tokens(12_000) and cli._format_tokens(12_000) == "12k"
    assert cli._format_duration(10) == "under 1 min"
