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
def test_skill_text_teaches_design_points_and_the_trajectory(name):
    text = agent.skill_text(name)
    for needle in ("R1", "Q1", "design concern", "option", "design point", "trajectory", "budget",
                   "references/design-space.md", "./rationale/<id>.json", "ddspace rationale check", "candidates",
                   "ddspace rationale build", "ddspace-rationale/2", '"step"', '"verdict"'):
        assert needle in text, needle
    assert "never name a concern, option or relation" in text.lower()
    steps = _steps(text)
    assert steps.rfind("ddspace rationale build") > steps.rfind("ddspace rationale check")  # build comes last
    last = " ".join(re.split(r"\n\d+\. ", steps)[-1].split())
    assert "In interactive use (not in a study session), finish with `ddspace rationale build" in last


def test_search_skill_alternates_exploitation_and_exploration_within_the_budget():
    text = " ".join(agent.skill_text("ddspace-search").split())
    for needle in ('"seed"', "exploit", "explore", "at most **12 design points**", "never more than 20",
                   "explore at least once", "two to four `kept` points",
                   "do not propose a point you did not investigate"):
        assert needle in text, needle


def test_explain_skill_finds_regions_and_stops_when_grounded():
    text = " ".join(agent.skill_text("ddspace-explain").split())
    for needle in ('"solution"', '"region"', '"contrast"', "partial design point", "one to three", "grounded",
                   "at most **8 points or regions**", "never more than 12", "two or three steps", "solution_quote",
                   "forced", "freely"):
        assert needle in text, needle
    assert '"uncovered": []' in text and "nearest_dimension_id" not in text


@pytest.mark.parametrize("name", SKILLS)
def test_the_skill_text_names_no_space_command(name):
    """SKILL.md is the same in every condition: the space's commands and ids live in the reference only."""
    text = agent.skill_text(name)
    assert "ddspace query" not in text and "ddspace point" not in text
    assert "dimension_id" not in text and "v:" not in text
    assert "`ddspace rationale build rationale/<id>.json --out .`" in " ".join(text.split())


@pytest.mark.parametrize("name", SKILLS)
def test_the_reference_maps_the_skill_onto_the_space(name):
    text = agent.reference_text(name, where=" --graph space")
    flat = " ".join(text.split())
    assert agent.SKILL_MARKER in text
    for needle in ("a dimension", "a value of a dimension", "single keyword", "ddspace query search",
                   '`ddspace query values "<d:id>" --graph space`', "ddspace query evidence", "ddspace query relations",
                   '`ddspace point "<v:id>" "<v:id>" ... --graph space`', "attested_by", "graph_sha256",
                   "`ddspace rationale build rationale/<id>.json --graph space` (not `--out`)",
                   "exactly as `ddspace query` prints it"):
        assert needle in flat, needle
    point = " ".join(next(s for s in text.split("\n- ") if s.startswith("**Investigate")).split())
    assert "one LLM call" in point and "the wiki's own description" in point
    before, fallback = point.split("--no-llm", 1)  # --no-llm only once, as the fallback
    assert "--no-llm" not in fallback and "fails" in before and "no API key" in before


def test_the_explain_reference_lists_uncovered_decisions_and_offered_options():
    text = " ".join(agent.reference_text("ddspace-explain").split())
    assert "uncovered" in text and "nearest_dimension_id" in text
    assert "options the space offers" in text and "not options the designers considered" in text


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
def test_the_skill_skeleton_passes_the_structural_check(name, space):
    """The JSON skeleton of SKILL.md (no space) and of the reference (with one) is a valid ddspace-rationale/2 file."""
    from delvedspace import rationale

    text = agent.reference_text(name) if space else agent.skill_text(name)
    doc = json.loads(re.search(r"```json\n(.*?)```", text, re.S).group(1))
    assert doc["schema"] == rationale.SCHEMA and (doc["space"] is None) == (not space)
    assert doc["mode"] == ("search" if name == "ddspace-search" else "explain")
    if space:
        points = [s["point"] for s in doc["trajectory"]]
        assert points and all(set(p) == {"description", "attested_by"} for p in points), points
    result = rationale.check(doc)
    assert result["ok"], result["problems"]
