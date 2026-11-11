"""``ddspace agent setup --skills``: the ddspace-search and ddspace-explain skills and their space reference."""

import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from delvedspace import agent
from tests.unit_tests.test_ddspace_query_agent import (  # noqa: F401  (fixtures)
    INSTALL,
    _installed,
    _invoke,
    ws,
)

SKILLS = ("ddspace-search", "ddspace-explain")
DIRS = (".claude/skills", ".agents/skills")
REPO = Path(__file__).resolve().parents[2]


def _front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert match, text[:200]
    return yaml.safe_load(match.group(1))


def _skill_files(root):
    return [root / d / name / "SKILL.md" for d in DIRS for name in SKILLS]


def test_setup_writes_both_skills_for_claude_code_and_codex(ws):
    result = _invoke("agent", "setup", "--skills", "--yes")
    assert result.exit_code == 0, result.output
    for path in _skill_files(ws.root):
        assert path.is_file(), path
        meta = _front_matter(path.read_text())
        assert meta["name"] == path.parent.name and meta["description"].strip()
        assert f"{path.parent.parent.parent.name}/skills/{path.parent.name}/SKILL.md" in result.output.replace("\n", "")


def test_setup_without_skills_writes_none(ws):
    assert _invoke("agent", "setup", "--yes").exit_code == 0
    assert not any(p.exists() for p in _skill_files(ws.root))


def test_no_space_needs_skills(ws):
    assert _invoke("agent", "setup", "--no-space", "--yes").exit_code == 1


def _steps(text):
    return text.split("## Steps", 1)[1].split("\n## ", 1)[0]


@pytest.mark.parametrize("name", SKILLS)
def test_skill_text_works_in_design_space_terms(name):
    text = agent.skill_text(name)
    flat = " ".join(text.split())
    for needle in ("R1", "Q1", "**dimension**", "**value**", "**relation**", "**design point**", "trajectory",
                   "budget", "references/design-space.md", "./rationale/<id>.json", "ddspace rationale check",
                   "candidates", "ddspace rationale build", "ddspace-rationale/6", "`points`", "reuse", "`adrs`", "`pros`", "`cons`", "`discarded`", '"step"', '"hypothesis"',
                   '"assessment"', '"observation"', "zero-shot", '"space": null', "`Dimension: Value`", "your own knowledge"):
        assert needle in flat, needle
    assert "every value in the file is an id: of the space, or, without one, a `dimension: value` name" in flat.lower()
    assert "you do not build or write a space" in flat and "space.dimensions" not in flat
    steps = _steps(text)
    assert steps.rfind("ddspace rationale build") > steps.rfind("ddspace rationale check")  # build comes last
    last = " ".join(re.split(r"\n\d+\. ", steps)[-1].split())
    assert "In interactive use (not in a study session), when `ddspace` is installed, finish with `ddspace rationale build" in last


def test_search_skill_runs_rounds_over_approaches_within_the_budget():
    text = " ".join(agent.skill_text("ddspace-search").split())
    for needle in ('"seed"', '"exploit"', '"explore"', '"ablate"', "at most **12 design points**",
                   "never more than 20", "what if", "diverge", "three rounds", "**Strong:** refine it",
                   "**Mixed:** keep the values that worked", "**Weak:** drop the approach",
                   "every round but the last", "after at least two rounds",
                   "beats on some requirement without being worse on any", "costs nothing",
                   "do not propose a point you did not evaluate"):
        assert needle in text, needle


def test_explain_skill_finds_regions_and_forced_values():
    text = " ".join(agent.skill_text("ddspace-explain").split())
    for needle in ('"solution"', '"region"', '"contrast"', "partial design point", "one to three", "grounded",
                   "at most **8 points or regions**", "never more than 12", "two or three steps", "solution_quote",
                   "**force**", "**freely**", '"forced"'):
        assert needle in text, needle
    assert '"uncovered": []' in text and '"unaddressed": []' in text and "Gaps in the space" in text
    assert "With a space, use it as it is" in text and '"fit": "approximate"' in text
    assert "Without a space there is nothing to fall short of" in text


@pytest.mark.parametrize("name", SKILLS)
def test_the_skill_text_names_no_space_command(name):
    """SKILL.md is the same in every condition: the space's commands live in the reference only. The one
    exception is ``ddspace point --no-space``, which describes a zero-shot point."""
    text = " ".join(agent.skill_text(name).split())
    assert "ddspace query" not in text
    assert text.count("ddspace point") == text.count("ddspace point --no-space") >= 1
    assert "`ddspace rationale build rationale/<id>.json --out .`" in " ".join(text.split())


@pytest.mark.parametrize("name", SKILLS)
def test_the_reference_maps_the_operations_onto_commands(name):
    text = agent.reference_text(name, where=" --graph space")
    flat = " ".join(text.split())
    assert agent.SKILL_MARKER in text
    for needle in ("| Operation in the skill | Command |", "one keyword per call",
                   '`ddspace query dimensions --graph space`', '`ddspace query values "<d:id>" --graph space`',
                   "ddspace query evidence", "ddspace query relations", "ddspace query search",
                   '`ddspace point "<v:id>" "<v:id>" ... --graph space`', "attested_by", "graph_sha256",
                   "`ddspace rationale build rationale/<id>.json --graph space` (not `--out`)",
                   "exactly as `ddspace query` prints it", "never `Dimension: Value` names"):
        assert needle in flat, needle
    assert "one LLM call" in flat and "the wiki's own description" in flat
    before, fallback = flat.split("--no-llm", 1)  # --no-llm only once, as the fallback
    assert "--no-llm" not in fallback and "fails" in before[-400:] and "no API key" in before[-400:]


def test_skills_from_a_parent_folder_point_commands_at_the_workspace(ws):
    parent = ws.root.parent
    assert _invoke("agent", "setup", "--skills", "--dir", str(parent), "--yes").exit_code == 0
    text = (parent / ".claude" / "skills" / "ddspace-search" / agent.REFERENCE).read_text()
    assert 'ddspace query dimensions --graph space' in text
    assert "ddspace rationale check rationale/<id>.json --graph space" in text


def _references(root):
    return [root / d / name / agent.REFERENCE for d in DIRS for name in SKILLS]


def test_setup_writes_the_reference_only_with_a_space(ws):
    assert _invoke("agent", "setup", "--skills", "--yes").exit_code == 0
    with_space = [p.read_text() for p in _skill_files(ws.root)]
    assert all(p.is_file() for p in _references(ws.root))
    assert _invoke("agent", "setup", "--skills", "--no-space", "--yes").exit_code == 0
    assert [p.read_text() for p in _skill_files(ws.root)] == with_space   # one SKILL.md for every condition
    assert not any(p.exists() for p in _references(ws.root))
    assert not any((ws.root / d / name / "references").exists() for d in DIRS for name in SKILLS)


def test_a_no_space_setup_keeps_a_reference_of_the_users_own(ws):
    mine = ws.root / ".claude" / "skills" / "ddspace-search" / agent.REFERENCE
    mine.parent.mkdir(parents=True)
    mine.write_text("# my notes on the space\n")
    assert _invoke("agent", "setup", "--skills", "--no-space", "--yes").exit_code == 0
    assert mine.read_text() == "# my notes on the space\n"


def test_rerun_updates_the_skills_in_place(ws):
    assert _invoke("agent", "setup", "--skills", "--no-space", "--yes").exit_code == 0
    assert _invoke("agent", "setup", "--skills", "--yes").exit_code == 0
    for path in _skill_files(ws.root):
        assert sorted(p.name for p in path.parent.iterdir()) == ["SKILL.md", "references"]
        text = path.read_text()
        assert text.count("\n---\n") == 1 and text.startswith("---\n")    # one front matter, not two
    for d in DIRS:
        assert sorted(p.name for p in (ws.root / d).iterdir()) == sorted(SKILLS)


def test_purge_removes_the_skills_it_wrote_and_nothing_else(ws):
    assert _invoke("agent", "setup", "--skills", "--claude", "--yes").exit_code == 0
    mine = ws.root / ".agents" / "skills" / "my-skill" / "SKILL.md"
    mine.parent.mkdir(parents=True)
    mine.write_text("---\nname: my-skill\ndescription: mine\n---\n")
    result = _invoke("reset", "--purge", "--yes")
    assert result.exit_code == 0, result.output
    assert not any(p.exists() for p in _skill_files(ws.root))
    assert mine.is_file()                                                   # the user's own skill stays
    assert not (ws.root / ".claude").exists()                               # emptied, so removed


def test_purge_removes_empty_skill_folders(ws):
    assert _invoke("agent", "setup", "--skills", "--yes").exit_code == 0
    assert _invoke("reset", "--purge", "--yes").exit_code == 0
    assert not (ws.root / ".agents").exists() and not (ws.root / ".claude").exists()


def test_skill_templates_ship_in_the_wheel(tmp_path):
    """pyproject package-data must list templates/skills/*/* (the templates/* glob is not recursive)."""
    if shutil.which("git") is None:
        pytest.skip("no git")
    out, src = tmp_path / "wheel", tmp_path / "src"
    files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "--", "pyproject.toml", "README.md",
                            "LICENSE", "src"], cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
    for rel in files:                                   # a copy of the source tree, so the repo is not touched
        if (REPO / rel).is_file():
            (src / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, src / rel)
    proc = subprocess.run([sys.executable, "-m", "pip", "wheel", str(src), "--no-deps", "--no-build-isolation",
                           "-q", "-w", str(out)], capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        pytest.skip(f"wheel build unavailable: {proc.stderr[-500:]}")
    wheel = next(out.glob("*.whl"))
    names = zipfile.ZipFile(wheel).namelist()
    for name in SKILLS:
        for rel in ("SKILL.md.j2", "references/design-space.md.j2"):
            assert f"delvedspace/templates/skills/{name}/{rel}" in names, [n for n in names if "templates" in n]


@pytest.mark.parametrize("space", [True, False])
@pytest.mark.parametrize("name", SKILLS)
def test_the_skill_skeleton_passes_the_check(name, space):
    """SKILL.md's JSON skeleton is a valid zero-shot ddspace-rationale/6 file (``space: null``, names for ids);
    with the names written as ids (``<dimension 1>`` -> ``d:1``) and the reference's
    ``space`` and ``points`` (descriptions and sources as ``ddspace point`` printed them) it is a valid file that
    names a wiki."""
    from delvedspace import rationale

    doc = json.loads(re.search(r"```json\n(.*?)```", agent.skill_text(name), re.S).group(1))
    assert doc["schema"] == rationale.SCHEMA and rationale.zero_shot(doc)
    assert doc["mode"] == ("search" if name == "ddspace-search" else "explain")
    assert [s["point"] for s in doc["trajectory"]] == [p["id"] for p in doc["points"]]
    if space:
        named = json.dumps(doc)
        named = re.sub(r"<dimension (\d+)>: <value (\d+\.\d+)>", r"v:\2", named)
        doc = json.loads(re.sub(r"<dimension (\d+)>", r"d:\1", named))
        ref = json.loads(re.search(r"```json\n(.*?)```", agent.reference_text(name), re.S).group(1))
        (listed,) = ref["points"]
        assert set(listed) == {"id", "values", "description", "attested_by"}
        assert ref["trajectory"][0]["values"] == doc["trajectory"][0]["values"] == listed["values"]
        assert ref["trajectory"][0]["point"] == listed["id"] == doc["points"][0]["id"]
        assert ref["alternatives"][0]["step"] == doc["alternatives"][0]["step"]
        doc["space"] = ref["space"]
        doc["points"][0] = listed
        assert rationale.names_space(doc)
    result = rationale.check(doc)
    assert result["ok"], result["problems"]


def test_zero_shot_skills_install_outside_a_workspace(tmp_path, monkeypatch):
    from typer.testing import CliRunner
    from delvedspace import cli
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["agent", "setup", "--skills", "--no-space", "--claude", "--yes"])
    assert result.exit_code == 0, result.output
    for folder in (".agents", ".claude"):
        for name in agent.SKILLS:
            skill = tmp_path / folder / "skills" / name
            assert (skill / "SKILL.md").is_file() and not (skill / agent.REFERENCE).exists()
    rules = json.loads((tmp_path / ".claude" / "settings.json").read_text())["permissions"]["allow"]
    assert any("point" in r for r in rules) and any("rationale" in r for r in rules)
    assert not (tmp_path / "AGENTS.md").exists()                     # no space to describe
    with_space = CliRunner().invoke(cli.app, ["agent", "setup", "--skills", "--yes"])
    assert with_space.exit_code != 0 and "ddspace.yaml" in with_space.output   # a space needs a workspace


@pytest.mark.parametrize("name", SKILLS)
def test_a_standalone_skill_finds_its_space_and_works_without_ddspace(name):
    text = " ".join(agent.skill_text(name).split())
    assert "A design space exists only when that command prints one" in text      # the folder, not the install
    assert "`ddspace` is not installed, keep the description `null`" in text
    assert "If `ddspace` is not installed, check the file yourself" in text
    assert "when `ddspace` is installed, finish with `ddspace rationale build" in text
    reference = agent.skill_files(name, space=True)[agent.REFERENCE]
    assert "the working folder is a `ddspace` workspace" in " ".join(reference.split()) and "mined" not in reference
