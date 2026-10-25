"""ddspace query (JSON and tables over raw/graph.json) and ddspace agent setup (AGENTS.md and pointers)."""

import json
import re
import shlex

import pytest
from typer.testing import CliRunner

from delvedspace import agent, cli
from delvedspace.workspace import Workspace
from taxonomy_generator.wiki import build, write
from tests.unit_tests.test_wiki_export import CORPUS, POINTS, _inputs

runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A workspace whose wiki is the synthetic export; the current folder is its root."""
    root = tmp_path / "proj" / "space"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    write(build(_inputs(design_points=POINTS)), root, "toy")
    (root / "corpus.json").write_text(json.dumps(list(CORPUS.values())))
    monkeypatch.chdir(root)
    return Workspace(root)


def test_query_prints_json_by_default(ws):
    result = _invoke("query", "dims")
    assert result.exit_code == 0, result.output
    assert {d["label"] for d in json.loads(result.output)} == {"Source of truth", "Replication"}


def test_query_table_for_people(ws):
    result = _invoke("query", "values", "Source of truth", "--table")
    assert result.exit_code == 0 and "WAL in S3" in result.output and "mixed" in result.output


def test_query_not_found_exits_2_with_candidates(ws):
    result = _invoke("query", "values", "Replicaton")
    assert result.exit_code == 2
    payload = json.loads(result.stdout[result.stdout.index("{"):])
    assert payload["candidates"][0]["label"] == "Replication"


def test_query_outside_a_workspace_needs_graph(tmp_path, monkeypatch, ws):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert _invoke("query", "info").exit_code == 1
    result = _invoke("query", "info", "--graph", str(ws.root))
    assert result.exit_code == 0 and json.loads(result.output)["run"] == "20261008_000000"


def test_evidence_quotes_come_from_the_workspace_corpus(ws):
    result = _invoke("query", "evidence", "WAL in S3", "--quotes")
    assert result.exit_code == 0, result.output
    texts = [p["text"] for s in json.loads(result.output)["sources"] for p in s["passages"]]
    assert "Continuity writes a WAL to S3." in texts


def test_evidence_quotes_refused_when_the_wiki_has_none(ws):
    ws.set("wiki.quotes", False)
    result = _invoke("query", "evidence", "WAL in S3", "--quotes")
    assert result.exit_code == 1 and "without quotes" in result.output


@pytest.mark.parametrize("command", [["info"], ["relations", "--table"], ["show", "WAL in S3", "--table"],
                                     ["search", "replica"], ["dims", "--core", "--table"], ["info", "--table"],
                                     ["evidence", "Disk quorum", "--table"]])
def test_every_subcommand_runs(ws, command):
    result = _invoke("query", *command)
    assert result.exit_code == 0, result.output


# ---------------------------------------------------------------- agent setup


INSTALL = {"path": "/opt/envs/toy/bin/ddspace", "activate": "conda activate toy"}


@pytest.fixture(autouse=True)
def _installed(monkeypatch):
    """Setup records where ddspace lives; pin it so the guide and the allow rules are predictable."""
    monkeypatch.setattr(agent, "install_info", lambda: dict(INSTALL))


def _guide_commands(text):
    block = re.search(r"## Query commands.*?```bash\n(.*?)```", text, re.S).group(1)
    return [shlex.split(line.split("#")[0])[1:] for line in block.splitlines() if line.startswith("ddspace query")]


def test_agents_md_examples_use_real_names_and_run(ws):
    result = _invoke("agent", "setup", "--yes")
    assert result.exit_code == 0, result.output
    text = (ws.root / "AGENTS.md").read_text()
    assert "<dimension>" not in text and "Source of truth" in text and "cite" in text.lower()
    assert "`exclusivity`" in text and "`includes`" in text                 # the fields dims and values return
    commands = _guide_commands(text)
    assert len(commands) == 7
    for args in commands:
        assert _invoke(*args).exit_code == 0, args


def test_guide_teaches_sketching_a_design_with_points(ws):
    assert _invoke("agent", "setup", "--yes").exit_code == 0
    text = (ws.root / "AGENTS.md").read_text()
    section = re.search(r"## Sketching a design\n(.*?)\n## ", text, re.S).group(1)
    assert "ddspace point" in section and "--no-llm" in section and "at least two alternatives" in section
    assert "value id" in section and "cite passage ids" in text


def test_guide_for_an_imported_expert_model_drops_passage_citations(tmp_path, monkeypatch):
    root = tmp_path / "expert"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    monkeypatch.chdir(root)
    model = {"decisions": [{"id": "a", "name": "Data storage", "question": "Where is data stored?"},
                           {"id": "b", "name": "Data access", "question": "How is data accessed?"}],
             "options": [{"id": "x", "name": "Data lake", "decision_ids": ["a"]},
                         {"id": "y", "name": "Data warehouse", "decision_ids": ["a"]},
                         {"id": "z", "name": "Direct access", "decision_ids": ["b"]}]}
    (tmp_path / "gt_model.json").write_text(json.dumps(model))
    assert _invoke("import", str(tmp_path / "gt_model.json"), "--kind", "decision-model", "--yes").exit_code == 0
    assert _invoke("wiki", "build", "--yes", "--no-llm").exit_code == 0
    assert _invoke("agent", "setup", "--yes").exit_code == 0
    text = (root / "AGENTS.md").read_text()
    assert "expert decision model" in text and "Data storage" in text
    assert "cite passage ids" not in text and "query evidence" not in text
    assert "## Sketching a design" in text and "dimension and value ids" in text


def test_setup_from_a_parent_folder_points_commands_at_the_workspace(ws, monkeypatch):
    parent = ws.root.parent
    assert _invoke("agent", "setup", "--dir", str(parent), "--yes").exit_code == 0
    text = (parent / "AGENTS.md").read_text()
    assert "--graph space" in text and "space/wiki/" in text
    monkeypatch.chdir(parent)
    for args in _guide_commands(text):
        assert _invoke(*args).exit_code == 0, args


def test_setup_refuses_a_folder_outside_the_workspace(ws, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    assert _invoke("agent", "setup", "--dir", str(other), "--yes").exit_code == 1


def test_setup_keeps_existing_content_and_replaces_its_own_block(ws):
    (ws.root / "AGENTS.md").write_text("# Team notes\n\nKeep me.\n")
    _invoke("agent", "setup", "--yes")
    _invoke("agent", "setup", "--yes")
    text = (ws.root / "AGENTS.md").read_text()
    assert text.startswith("# Team notes") and "Keep me." in text
    assert text.count("<!-- ddspace:start -->") == 1


def test_claude_and_copilot_pointers_and_the_allow_rule(ws):
    settings = ws.root / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls:*)"]}, "model": "x"}))
    result = _invoke("agent", "setup", "--claude", "--copilot", "--yes")
    assert result.exit_code == 0, result.output
    assert "@AGENTS.md" in (ws.root / "CLAUDE.md").read_text()
    assert "AGENTS.md" in (ws.root / ".github" / "copilot-instructions.md").read_text()
    data = json.loads(settings.read_text())
    assert data["permissions"]["allow"] == ["Bash(ls:*)", "Bash(ddspace query:*)",
                                            "Bash(/opt/envs/toy/bin/ddspace query:*)"] and data["model"] == "x"
    _invoke("agent", "setup", "--claude", "--yes")
    assert json.loads(settings.read_text())["permissions"]["allow"].count("Bash(ddspace query:*)") == 1
    assert agent.disallow_query(settings) == "cleaned"                 # both rules go, the user's stays
    assert json.loads(settings.read_text())["permissions"]["allow"] == ["Bash(ls:*)"]


def test_guide_says_how_to_reach_ddspace_when_the_shell_lacks_it(ws):
    assert _invoke("agent", "setup", "--yes").exit_code == 0
    text = (ws.root / "AGENTS.md").read_text()
    assert "ddspace --version" in text
    assert "/opt/envs/toy/bin/ddspace query info" in text                # the full path, any shell
    assert "conda activate toy && ddspace query info" in text            # or activate in the same command
    bare = agent.guide(ws, ws.root, {"path": None, "activate": None})
    assert "ask the user which environment" in bare and "&& ddspace" not in bare


def test_no_allow_rule_when_declined(ws):
    assert _invoke("agent", "setup", "--claude", "--no-allow-query").exit_code == 0
    assert not (ws.root / ".claude" / "settings.json").exists()


def test_setup_before_the_wiki_exists_explains(tmp_path, monkeypatch):
    root = tmp_path / "fresh"
    _invoke("init", str(root), "--yes")
    monkeypatch.chdir(root)
    result = _invoke("agent", "setup", "--yes")
    assert result.exit_code == 0 and "ddspace wiki build" in result.output
    assert "not been built yet" in (root / "AGENTS.md").read_text()


def test_evidence_quotes_follow_graph_from_the_parent_folder(ws, monkeypatch):
    monkeypatch.chdir(ws.root.parent)
    for graph in (ws.root, ws.root / "raw" / "graph.json"):
        result = _invoke("query", "evidence", "WAL in S3", "--graph", str(graph), "--quotes")
        assert result.exit_code == 0, result.output
        texts = [p["text"] for s in json.loads(result.output)["sources"] for p in s["passages"]]
        assert "Continuity writes a WAL to S3." in texts


def _quote_texts(*args):
    result = _invoke("query", "evidence", "WAL in S3", "--quotes", *args)
    assert result.exit_code == 0, result.output
    return [p["text"] for s in json.loads(result.output)["sources"] for p in s["passages"]]


def test_evidence_quotes_come_from_the_run_corpus(ws):
    run_dir = ws.runs_dir / "20261008_000000"      # the run the synthetic wiki was built from
    run_dir.mkdir(parents=True)
    (run_dir / "corpus.json").write_text(json.dumps(list(CORPUS.values())))
    ws.corpus_path.write_text(json.dumps([{**p, "text": "changed later"} for p in CORPUS.values()]))
    assert "Continuity writes a WAL to S3." in _quote_texts()
    assert "changed later" not in _quote_texts()


def test_evidence_quotes_fall_back_to_the_workspace_corpus_without_a_run_snapshot(ws):
    (ws.runs_dir / "20261008_000000").mkdir(parents=True)
    assert "Continuity writes a WAL to S3." in _quote_texts()
