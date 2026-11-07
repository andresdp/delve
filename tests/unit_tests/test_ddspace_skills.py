"""``ddspace agent setup --skills``: the ddspace-search and ddspace-explain skills, with and without a space."""

import difflib
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


@pytest.mark.parametrize("name", SKILLS)
def test_skill_text_teaches_the_workflow(name):
    text = agent.skill_text(name, space=True)
    for needle in ("R1", "Q1", "C1", "single keyword", "ddspace query search", "ddspace query values",
                   "ddspace query evidence", "ddspace query relations", "ddspace point", "--no-llm",
                   "./rationale/<id>.json", "exactly as `ddspace query` prints them", "ddspace rationale check",
                   "candidates", "ddspace rationale build", "ddspace-rationale/1"):
        assert needle in text, needle
    assert "never name a dimension, value or relation" in text.lower()
    steps = text.split("## Steps", 1)[1].split("\n## ", 1)[0]
    assert steps.rfind("ddspace rationale build") > steps.rfind("ddspace rationale check")  # build comes last
    last = " ".join(re.split(r"\n\d+\. ", steps)[-1].split())
    assert "In interactive use (not in a study session), finish with `ddspace rationale build" in last


def test_explain_skill_quotes_the_solution_and_lists_uncovered_decisions():
    text = agent.skill_text("ddspace-explain", space=True)
    assert "solution_quote" in text and "uncovered" in text and '"S"' in text
    assert "options the space offers" in text and "not options the designers considered" in text
    bare = agent.skill_text("ddspace-explain", space=False)
    assert "solution_quote" in bare and '"uncovered": []' in bare
    assert "nearest_dimension_id" not in bare


@pytest.mark.parametrize("name", SKILLS)
def test_no_space_variant_drops_only_the_space_steps(name):
    full, bare = agent.skill_text(name, space=True), agent.skill_text(name, space=False)
    assert "ddspace query" not in bare and "ddspace point" not in bare
    assert "ddspace rationale check" in bare and '"space": null' in bare
    assert _front_matter(bare)["name"] == name
    # Apart from the space steps, the variants are the same text: every difference is about the space.
    strip = lambda t: [re.sub(r"^\d+\. ", "", line) for line in t.splitlines()]  # noqa: E731  (renumbered steps)
    a, b = strip(full), strip(bare)
    space_only = re.compile(r"ddspace query|ddspace point|dimension_id|value_id|`d:|`v:|space|uncovered|passage|"
                            r"evidence|graph_sha256|--graph|relation")
    no_space_only = re.compile(r"decision|option|space|uncovered|relations")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        removed, added = "\n".join(a[i1:i2]), "\n".join(b[j1:j2])
        assert not removed.strip() or space_only.search(removed), removed
        assert not added.strip() or no_space_only.search(added), added


def test_skills_from_a_parent_folder_point_commands_at_the_workspace(ws):
    parent = ws.root.parent
    assert _invoke("agent", "setup", "--skills", "--dir", str(parent), "--yes").exit_code == 0
    text = (parent / ".claude" / "skills" / "ddspace-search" / "SKILL.md").read_text()
    assert 'ddspace query dimensions --graph space' in text
    assert "ddspace rationale check rationale/<id>.json --graph space" in text


def test_no_space_setup_writes_the_no_space_variant(ws):
    assert _invoke("agent", "setup", "--skills", "--no-space", "--yes").exit_code == 0
    for path in _skill_files(ws.root):
        text = path.read_text()
        assert "ddspace query" not in text and "ddspace rationale check" in text


def test_rerun_updates_the_skills_in_place(ws):
    assert _invoke("agent", "setup", "--skills", "--no-space", "--yes").exit_code == 0
    assert _invoke("agent", "setup", "--skills", "--yes").exit_code == 0
    for path in _skill_files(ws.root):
        assert sorted(p.name for p in path.parent.iterdir()) == ["SKILL.md"]
        text = path.read_text()
        assert text.count("\n---\n") == 1 and text.startswith("---\n")    # one front matter, not two
        assert "ddspace query search" in text                               # the with-space variant now
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
        assert f"delvedspace/templates/skills/{name}/SKILL.md.j2" in names, [n for n in names if "templates" in n]


@pytest.mark.parametrize("space", [True, False])
@pytest.mark.parametrize("name", SKILLS)
def test_the_skill_skeleton_passes_the_structural_check(name, space):
    """The JSON skeleton each skill shows is a valid ddspace-rationale/1 file (structure only, no graph)."""
    from delvedspace import rationale

    block = re.search(r"```json\n(.*?)```", agent.skill_text(name, space=space), re.S).group(1)
    doc = json.loads(block)
    assert doc["schema"] == "ddspace-rationale/1" and (doc["space"] is None) == (not space)
    assert doc["mode"] == ("search" if name == "ddspace-search" else "explain")
    result = rationale.check(doc)
    assert result["ok"], result["problems"]
