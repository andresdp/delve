"""OKF v0.2 bundle: page types, stance, bundle links, index files, kept log, and the conformance check."""

import re

import pytest
import yaml

from taxonomy_generator.wiki import build, okf, write
from tests.unit_tests.test_wiki_export import POINTS, _inputs, _taxonomy


def _front(path):
    m = re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S)
    return yaml.safe_load(m.group(1)) if m else None


@pytest.fixture
def out(tmp_path):
    write(build(_inputs(design_points=POINTS)), tmp_path / "x", "toy", html_dir="site", okf_by="delvedspace/0.1.0")
    return tmp_path / "x"


def test_bundle_passes_the_check_without_broken_links(out):
    errors, warnings = okf.check(out / "wiki")
    assert errors == [] and warnings == []


def test_layout_has_site_and_no_wikilink_files(out):
    assert (out / "site" / "graph.html").is_file() and not (out / "html").exists()
    assert not (out / ".llmwiki.yaml").exists() and not (out / "SCHEMA.md").exists()
    assert (out / "raw" / "graph.json").is_file() and (out / "raw" / "run.json").is_file()
    assert not list((out / "wiki").rglob("*.md")) or not any("[[" in p.read_text() for p in (out / "wiki").rglob("*.md"))


def test_descriptive_types_stance_and_generated(out):
    wiki = out / "wiki"
    assert _front(wiki / "concepts" / "source-of-truth.md")["type"] == "Design Decision"
    wal = _front(wiki / "entities" / "wal-in-s3.md")
    assert wal["type"] == "Design Alternative" and wal["stance"] == "mixed" and "status" not in wal
    assert wal["dimension"] == "/concepts/source-of-truth.md"
    assert wal["description"] == "WAL in S3 description."
    assert wal["generated"]["by"] == "delvedspace/0.1.0" and re.search(r"[+-]\d\d:\d\d$", wal["generated"]["at"])
    assert _front(wiki / "entities" / "lower-latency.md")["type"] == "Outcome"
    overview = _front(wiki / "overview.md")
    assert overview["type"] == "Overview" and "sources" not in overview


def test_index_files_follow_section_8(out):
    wiki = out / "wiki"
    root = (wiki / "index.md").read_text()
    assert _front(wiki / "index.md") == {"okf_version": "0.2"}
    assert "* [Design decisions (dimensions)](/concepts/index.md) - 2 pages" in root
    assert "[toy](/overview.md)" in root
    concepts = (wiki / "concepts" / "index.md").read_text()
    assert _front(wiki / "concepts" / "index.md") is None
    assert "* [Source of truth](/concepts/source-of-truth.md) - Where does the truth live?" in concepts


def test_log_md_survives_a_rebuild(out):
    (out / "wiki" / "log.md").write_text("# Log\n\n## 2026-10-13\n\n- **Creation** first build.\n")
    write(build(_inputs(design_points=POINTS)), out, "toy", html_dir="site", okf_by="delvedspace/0.1.0")
    assert "first build" in (out / "wiki" / "log.md").read_text()


def test_default_export_is_unchanged_wikilink_layout(tmp_path):
    write(build(_inputs()), tmp_path / "y", "toy")
    assert (tmp_path / "y" / "SCHEMA.md").is_file() and (tmp_path / "y" / "html").is_dir()
    assert "[[" in (tmp_path / "y" / "wiki" / "entities" / "wal-in-s3.md").read_text()


@pytest.mark.parametrize("rel, text, problem", [
    ("concepts/a.md", "# no frontmatter\n", "no YAML frontmatter"),
    ("concepts/b.md", "---\ntitle: B\n---\n\nbody\n", "no `type`"),
    ("concepts/c.md", "---\ntype: [unclosed\n---\n\nbody\n", "not valid YAML"),
    ("concepts/index.md", "---\ntitle: x\n---\n\n# X\n\n* [A](/a.md)\n", "no frontmatter"),
    ("sources/index.md", "Just text.\n", "no section heading"),
    ("log.md", "# Log\n\n## 2026-10-01\n\n- a\n\n## 2026-10-05\n\n- b\n", "newest first"),
    ("log.md", "# Log\n\n## October 5\n\n- a\n", "YYYY-MM-DD"),
])
def test_check_reports_each_violation(tmp_path, rel, text, problem):
    path = tmp_path / "w" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    errors, _ = okf.check(tmp_path / "w")
    assert any(problem in e for e in errors), errors


def test_broken_links_are_only_warnings(tmp_path):
    page = tmp_path / "w" / "concepts" / "a.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\ntype: Design Decision\n---\n\nSee [missing](/concepts/nope.md).\n")
    errors, warnings = okf.check(tmp_path / "w")
    assert errors == [] and warnings == ["concepts/a.md: broken link /concepts/nope.md"]


def test_reserved_slugs_get_a_suffix(tmp_path):
    tax = _taxonomy()
    tax["selected_clusters"][0]["values"][0]["label"] = "Index"
    tax["selected_clusters"][1]["name"] = "Log"
    write(build(_inputs(taxonomy=tax)), tmp_path, "toy", okf_by="delvedspace/0.1.0")
    wiki = tmp_path / "wiki"
    assert (wiki / "entities" / "index-2.md").is_file() and (wiki / "concepts" / "log-2.md").is_file()
    assert okf.check(wiki)[0] == []
