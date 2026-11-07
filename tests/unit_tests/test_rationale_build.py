"""ddspace rationale build: a checked rationale file rendered as an explainer page, in a workspace or standalone."""

import json
import posixpath
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from delvedspace import cli
from taxonomy_generator.wiki import build, write
from tests.unit_tests.test_ddspace_rationale import _explain, _no_space, _sample
from tests.unit_tests.test_wiki_export import POINTS, _inputs

runner = CliRunner()
HREF = re.compile(r'href="([^"]+)"|"href": ?"([^"]+)"')


def _invoke(*args):
    return runner.invoke(cli.app, list(args))


def _wiki(root, html_dir="site"):
    write(build(_inputs(design_points=POINTS)), root, "toy", html_dir=html_dir)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A workspace whose wiki is the synthetic toy export, laid out as `ddspace wiki build` writes it (site/)."""
    root = tmp_path / "proj" / "space"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    _wiki(root)
    monkeypatch.chdir(root)
    return root


def _file(tmp_path, doc, name="r.json"):
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def _links(page: Path):
    """Every href in the page (markup and inlined data), except in-page anchors and the script's templates."""
    text = page.read_text(encoding="utf-8")
    return [a or b for a, b in HREF.findall(text) if not (a or b).startswith(("#", "http")) and "esc(" not in a + b]


def _wiki_links(page: Path):
    return [h for h in _links(page) if "/assets/" not in h and not h.startswith("assets/")]


def _resolves(page: Path, href: str) -> bool:
    return (page.parent / posixpath.normpath(href.split("#")[0])).resolve().is_file()


def _search_with_a_shared_dimension():
    """A1 and A2 both take Disk quorum on d:1 and differ on d:2 (A1 three-phase commit, A2 leaves it open)."""
    doc = _sample()
    doc["alternatives"][1]["choices"] = [
        {"dimension_id": "d:1", "value_id": "v:1.1", "drivers": ["Q1"], "reason": "Disks survive one failure.",
         "evidence": [{"doc": "s01_p01", "stance": "accepts"}], "solution_quote": None}]
    doc["comparison"] = [{"dimension_id": "d:2", "note": "A1 commits in three phases; A2 leaves it open."}]
    return doc


def _built(result):
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_search_with_two_alternatives_renders_tabs_compare_and_wiki_links(ws, tmp_path):
    before = json.loads((ws / "raw" / "exported.json").read_text(encoding="utf-8"))
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _search_with_a_shared_dimension()))))
    page = ws / "site" / "explainers" / "toy-store-search.html"
    assert Path(payload["page"]) == page and page.is_file()
    assert json.loads((ws / "rationale" / "toy-store-search.json").read_text(encoding="utf-8"))["id"] == \
        "toy-store-search"
    html = page.read_text(encoding="utf-8")
    assert html.count('class="tab"') == 3  # A1, A2 and the compare view
    assert 'data-tab="A1"' in html and 'data-tab="A2"' in html and 'data-tab="compare"' in html
    rows = re.findall(r'<tr class="row(?: differs)?" data-dimension="([^"]+)"', html)
    assert rows == ["d:2", "d:1"]  # the differing dimension first
    assert 'class="row differs" data-dimension="d:2"' in html
    assert "A1 commits in three phases" in html
    for req in ("R1", "Q1", "C1"):
        assert f'data-requirement="{req}"' in html
    # Evidence as passage ids with stances, never quotes.
    assert "s01_p01" in html and "accepts" in html
    links = _wiki_links(page)
    assert any(h.endswith("concepts/source-of-truth.html") for h in links)
    assert any(h.endswith("entities/disk-quorum.html") for h in links)
    assert any(h.endswith("sources/s1.html") for h in links)
    broken = [h for h in _links(page) if not _resolves(page, h)]
    assert not broken, broken
    assert '../assets/d3.min.js' in html and '../assets/style.css' in html
    # The export's manifest is left as the wiki build wrote it, so the next build neither lists nor removes the page.
    assert json.loads((ws / "raw" / "exported.json").read_text(encoding="utf-8")) == before


def test_the_page_survives_a_wiki_rebuild(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _sample()))))
    page = ws / "site" / "explainers" / "toy-store-search.html"
    _wiki(ws)  # what `ddspace wiki build` writes
    _wiki(ws)
    assert page.is_file()
    assert "site/index.html" in json.loads((ws / "raw" / "exported.json").read_text(encoding="utf-8"))


def test_explain_shows_uncovered_quotes_and_values_offered_by_the_space(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _explain()))))
    html = (ws / "site" / "explainers" / "toy-store-explain.html").read_text(encoding="utf-8")
    assert 'data-tab="compare"' not in html  # one alternative: no compare view
    assert "Backup schedule" in html and "nightly snapshots" in html and "Client library" in html
    assert "data stays on each node&#39;s disk" in html and "a three-phase commit" in html
    assert "offered by the space" in html
    assert "every decision mapped" not in html


def test_explain_with_nothing_uncovered_says_every_decision_mapped(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _explain(uncovered=0)))))
    html = (ws / "site" / "explainers" / "toy-store-explain.html").read_text(encoding="utf-8")
    assert "every decision mapped" in html


def test_no_space_with_out_writes_a_standalone_folder_without_wiki_links(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "out"
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _no_space())), "--out", str(out)))
    page = out / "explainers" / "toy-store-search.html"
    assert Path(payload["page"]) == page and page.is_file()
    assert (out / "assets" / "d3.min.js").is_file() and (out / "assets" / "style.css").is_file()
    assert _wiki_links(page) == []
    assert all(_resolves(page, h) for h in _links(page))
    html = page.read_text(encoding="utf-8")
    assert "Local disks" in html and "Postgres" in html and 'data-tab="compare"' in html


def test_no_space_without_out_is_a_usage_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = _invoke("rationale", "build", str(_file(tmp_path, _no_space())))
    assert result.exit_code == 2 and "--out" in json.loads(result.stdout)["error"]


def test_an_unknown_id_exits_1_and_writes_nothing(ws, tmp_path):
    before = (ws / "raw" / "exported.json").read_text(encoding="utf-8")
    doc = _sample()
    doc["alternatives"][0]["choices"][0]["value_id"] = "v:9.9"
    result = _invoke("rationale", "build", str(_file(tmp_path, doc)))
    assert result.exit_code == 1
    assert json.loads(result.stdout)["problems"][0]["code"] == "unknown_id"
    assert not (ws / "site" / "explainers").exists() and not (ws / "rationale" / "toy-store-search.json").exists()
    assert (ws / "raw" / "exported.json").read_text(encoding="utf-8") == before


def test_a_workspace_whose_html_is_in_html_renders_there(tmp_path, monkeypatch):
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    _wiki(root, html_dir="html")
    monkeypatch.chdir(root)
    _built(_invoke("rationale", "build", str(_file(tmp_path, _sample()))))
    page = root / "html" / "explainers" / "toy-store-search.html"
    assert page.is_file() and all(_resolves(page, h) for h in _links(page))


def test_a_space_file_with_out_links_to_the_wiki_it_was_checked_against(ws, tmp_path):
    out = tmp_path / "share"
    _built(_invoke("rationale", "build", str(_file(tmp_path, _sample())), "--out", str(out)))
    page = out / "explainers" / "toy-store-search.html"
    assert (out / "assets" / "d3.min.js").is_file()
    assert _wiki_links(page) and all(_resolves(page, h) for h in _links(page))
    assert not (ws / "site" / "explainers").exists()  # --out leaves the workspace alone


def test_a_changed_graph_shows_the_banner(ws, tmp_path):
    doc = _sample()
    doc["space"]["graph_sha256"] = "0" * 64
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, doc))))
    assert [p["code"] for p in payload["problems"]] == ["graph_changed"]
    html = Path(payload["page"]).read_text(encoding="utf-8")
    assert 'class="banner"' in html and "graph changed" in html.lower()
