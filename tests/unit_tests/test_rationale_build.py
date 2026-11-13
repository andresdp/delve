"""ddspace rationale build: a checked rationale file rendered as an explainer page, in a workspace or standalone."""

import json
import posixpath
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from delvedspace import cli, rationale
from taxonomy_generator.wiki import build, write
from taxonomy_generator.wiki import explainer
from tests.unit_tests.test_ddspace_rationale import _explain, _zero, _sample
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
    doc["trajectory"][2]["values"] = ["v:1.1"]
    doc["trajectory"][2]["point"] = "P2"   # the same point as step 2: reused, not described again
    doc["trajectory"][2]["tradeoffs"][0]["values"] = ["v:1.1"]
    del doc["points"][2]
    shared, other = doc["adrs"][0]["options"]
    shared["in"] = ["A1", "A2"]
    other.update(status="discarded", **{"in": []})
    del other["step"]
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
    assert html.count('class="tab"') == 3  # the ADRs, the comparison and the trajectory
    assert html.index('data-tab="adrs"') < html.index('data-tab="compare"') < html.index('data-tab="trajectory"')
    assert ">Comparison</button>" in html and "Composed of 2 partial design points" in html
    assert 'data-alt="A1"' in html and 'data-alt="A2"' in html
    assert 'data-option="ADR1:O1"' in html and "chosen in A1, A2" in html and 'class="option discarded"' in html
    assert '<li class="pro">' in html and '<li class="con">' in html
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
    # The page joins the export's manifest, since every wiki build renders it again.
    assert json.loads((ws / "raw" / "exported.json").read_text(encoding="utf-8")) == \
        sorted(before + ["site/explainers/toy-store-search.html"])


def test_an_export_given_explainers_renders_them_and_keeps_them_listed(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _sample()))))
    page = ws / "site" / "explainers" / "toy-store-search.html"
    for _ in range(2):  # what `ddspace wiki build` writes
        rendered = write(build(_inputs(design_points=POINTS)), ws, "toy", html_dir="site",
                         explainers=lambda html: rationale.render_workspace(ws, html))
        assert [(e["id"], e["status"]) for e in rendered] == [("toy-store-search", "ok")]
    assert page.is_file()
    assert "site/explainers/toy-store-search.html" in json.loads((ws / "raw" / "exported.json").read_text("utf-8"))
    _wiki(ws)  # an export that does not render explainers removes the page it listed
    assert not page.exists()


def test_explain_shows_uncovered_quotes_and_values_offered_by_the_space(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _explain()))))
    html = (ws / "site" / "explainers" / "toy-store-explain.html").read_text(encoding="utf-8")
    assert 'data-tab="compare"' not in html  # one alternative: no compare view
    assert "Backup schedule" in html and "nightly snapshots" in html and "Client library" in html
    assert "data stays on each node&#39;s disk" in html and "a three-phase commit" in html
    assert 'class="option chosen"' in html and 'class="option discarded"' in html
    assert "Every decision maps onto the space" not in html and "Gaps in the space" in html
    assert "2</strong> decisions not covered" in html and "the solution does not address it" in html


def test_explain_with_nothing_uncovered_says_every_decision_mapped(ws, tmp_path):
    _built(_invoke("rationale", "build", str(_file(tmp_path, _explain(uncovered=0)))))
    html = (ws / "site" / "explainers" / "toy-store-explain.html").read_text(encoding="utf-8")
    assert "Every decision maps onto the space" in html


def test_zero_shot_with_out_writes_a_standalone_folder_without_wiki_links(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "out"
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _zero())), "--out", str(out)))
    page = out / "explainers" / "toy-store-search.html"
    assert Path(payload["page"]) == page and page.is_file()
    assert (out / "assets" / "d3.min.js").is_file() and (out / "assets" / "style.css").is_file()
    assert _wiki_links(page) == []
    assert all(_resolves(page, h) for h in _links(page))
    html = page.read_text(encoding="utf-8")
    assert "Local disks" in html and "Postgres" in html and 'data-tab="compare"' in html


def test_zero_shot_without_out_is_a_usage_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = _invoke("rationale", "build", str(_file(tmp_path, _zero())))
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
    out = ws / "share"  # --out stays inside the current folder
    _built(_invoke("rationale", "build", str(_file(tmp_path, _sample())), "--out", str(out)))
    page = out / "explainers" / "toy-store-search.html"
    assert (out / "assets" / "d3.min.js").is_file()
    assert _wiki_links(page) and all(_resolves(page, h) for h in _links(page))
    # inside the space's own workspace, the page also goes into its wiki (agents pass --out by habit)
    assert (ws / "site" / "explainers" / "toy-store-search.html").is_file()
    assert (ws / "rationale" / "toy-store-search.json").is_file()


def test_out_with_graph_from_another_folder_leaves_that_workspace_alone(ws, tmp_path, monkeypatch):
    elsewhere = tmp_path / "results"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)                    # as the study runner does: --graph names the workspace
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _sample())), "--out", "explainers-x",
                             "--graph", str(ws)))
    assert (elsewhere / "explainers-x" / "explainers" / "toy-store-search.html").is_file()
    assert "wiki_page" not in payload and not (ws / "site" / "explainers").exists()


def test_a_changed_graph_shows_the_banner(ws, tmp_path):
    doc = _sample()
    doc["space"]["graph_sha256"] = "0" * 64
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, doc))))
    assert [p["code"] for p in payload["problems"]] == ["graph_changed"]
    html = Path(payload["page"]).read_text(encoding="utf-8")
    assert 'class="banner"' in html and "graph changed" in html.lower()


# ---------------------------------------------------------------- explainers in `ddspace wiki build`

import copy  # noqa: E402
import hashlib  # noqa: E402

from delvedspace.workspace import Workspace  # noqa: E402
from tests.unit_tests.test_ddspace_wiki import _add_run  # noqa: E402
from tests.unit_tests.test_wiki_export import CORPUS, _taxonomy  # noqa: E402

PAGE = "site/explainers/toy-store-search.html"


@pytest.fixture
def built(tmp_path, monkeypatch):
    """A workspace with a real `ddspace wiki build` (site/), the current folder its root."""
    root = tmp_path / "space"
    assert _invoke("init", str(root), "--yes", "--name", "toy").exit_code == 0
    monkeypatch.chdir(root)
    w = Workspace(root)
    w.corpus_path.write_text(json.dumps(list(CORPUS.values())))
    _add_run(w, "20261013_100000", _taxonomy())
    _wiki_build()
    return w


def _wiki_build():
    result = _invoke("wiki", "build", "--yes")
    assert result.exit_code == 0, result.output
    return result


def _current(root, doc=None):
    """``doc`` (the sample by default) with the hash of the workspace's current graph."""
    doc = copy.deepcopy(doc or _sample())
    doc["space"]["graph_sha256"] = hashlib.sha256((root / "raw" / "graph.json").read_bytes()).hexdigest()
    return doc


def _manifest(root):
    return json.loads((root / "raw" / "exported.json").read_text(encoding="utf-8"))


def _list(*extra):
    result = _invoke("rationale", "list", *extra)
    assert result.exit_code == 0, result.output
    return result


def _statuses():
    return {e["id"]: e["status"] for e in json.loads(_list().stdout)}


def test_rationale_build_then_two_wiki_builds_keep_the_page_listed(built, tmp_path):
    root = built.root
    _built(_invoke("rationale", "build", str(_file(tmp_path, _current(root)))))
    assert PAGE in _manifest(root)  # rationale build lists its page, as wiki build would
    _wiki_build()
    _wiki_build()
    assert (root / PAGE).is_file() and PAGE in _manifest(root)
    assert 'class="banner"' not in (root / PAGE).read_text(encoding="utf-8")  # same run: the graph is unchanged


def test_wiki_build_then_rationale_build_then_wiki_build_keeps_the_page(built, tmp_path):
    root = built.root
    _built(_invoke("rationale", "build", str(_file(tmp_path, _current(root)))))
    before = (root / PAGE).stat().st_mtime_ns
    _wiki_build()
    assert (root / PAGE).is_file() and PAGE in _manifest(root)
    assert (root / PAGE).stat().st_mtime_ns != before  # re-rendered by the build itself
    assert "site/index.html" in _manifest(root)


def test_a_broken_file_is_skipped_with_a_warning_and_its_old_page_removed(built, tmp_path):
    root = built.root
    _built(_invoke("rationale", "build", str(_file(tmp_path, _current(root)))))
    copied = root / "rationale" / "toy-store-search.json"
    doc = json.loads(copied.read_text(encoding="utf-8"))
    doc["alternatives"][0]["choices"][0]["value_id"] = "v:9.9"
    copied.write_text(json.dumps(doc), encoding="utf-8")
    result = _wiki_build()
    assert "toy-store-search" in result.output and "broken" in result.output
    assert not (root / PAGE).exists() and PAGE not in _manifest(root)
    assert copied.is_file()  # the file itself is the agent's: kept for it to fix
    assert "explainers/toy-store-search.html" not in (root / "site" / "index.html").read_text(encoding="utf-8")


def test_a_changed_graph_renders_the_banner_and_list_says_changed(built, tmp_path):
    root = built.root
    _built(_invoke("rationale", "build", str(_file(tmp_path, _current(root)))))
    assert _statuses() == {"toy-store-search": "ok"}
    tax = _taxonomy()
    tax["selected_clusters"][0]["description"] = "Where does the truth live now?"
    _add_run(built, "20261014_090000", tax)
    _wiki_build()
    html = (root / PAGE).read_text(encoding="utf-8")
    assert 'class="banner"' in html and "graph changed" in html.lower()
    assert _statuses() == {"toy-store-search": "changed"}


def test_list_reports_ok_changed_and_broken_files(built, tmp_path):
    root = built.root
    (root / "rationale").mkdir(exist_ok=True)
    good = _current(root)
    (root / "rationale" / "toy-store-search.json").write_text(json.dumps(good), encoding="utf-8")
    old = _current(root, _explain())
    old["space"]["graph_sha256"] = "0" * 64
    (root / "rationale" / "toy-store-explain.json").write_text(json.dumps(old), encoding="utf-8")
    bad = copy.deepcopy(good)
    bad.update(id="toy-store-bad")
    bad["alternatives"][0]["choices"][0]["dimension_id"] = "d:99"
    (root / "rationale" / "toy-store-bad.json").write_text(json.dumps(bad), encoding="utf-8")
    (root / "rationale" / "garbled.json").write_text("{ not json", encoding="utf-8")
    entries = {e["id"]: e for e in json.loads(_list().stdout)}
    assert {i: e["status"] for i, e in entries.items()} == {
        "toy-store-search": "ok", "toy-store-explain": "changed", "toy-store-bad": "broken", "garbled": "broken"}
    assert entries["toy-store-search"]["mode"] == "search" and entries["toy-store-search"]["alternatives"] == 2
    assert entries["toy-store-explain"]["mode"] == "explain" and entries["toy-store-explain"]["alternatives"] == 1
    assert entries["toy-store-search"]["page"] is None  # not rendered yet
    _wiki_build()
    entries = {e["id"]: e for e in json.loads(_list().stdout)}
    assert Path(entries["toy-store-search"]["page"]) == root / PAGE and (root / PAGE).is_file()
    assert entries["toy-store-bad"]["page"] is None
    table = _list("--table").stdout
    assert "toy-store-bad" in table and "broken" in table and "changed" in table


def test_the_html_index_lists_explainers_only_when_any_exist(built, tmp_path):
    root = built.root
    index = root / "site" / "index.html"
    assert "Explainers" not in index.read_text(encoding="utf-8")
    _built(_invoke("rationale", "build", str(_file(tmp_path, _current(root)))))
    html = index.read_text(encoding="utf-8")
    assert "Explainers" in html and 'href="explainers/toy-store-search.html"' in html
    assert "A durable key-value store for a small cluster" in html
    _wiki_build()
    html = index.read_text(encoding="utf-8")
    assert "Explainers" in html and 'href="explainers/toy-store-search.html"' in html
    assert "Explainers" not in (root / "wiki" / "index.md").read_text(encoding="utf-8")  # the OKF bundle is unchanged


# ---------------------------------------------------------------- review fixes

from taxonomy_generator.wiki import explainer  # noqa: E402


def _put(root, name, doc):
    folder = root / "rationale"
    folder.mkdir(exist_ok=True)
    path = folder / name
    path.write_text(doc if isinstance(doc, str) else json.dumps(doc), encoding="utf-8")
    return path


def _by_file(stdout):
    return {Path(e["file"]).name: e for e in json.loads(stdout)}


def test_two_files_with_one_id_are_both_broken_and_neither_is_rendered(ws):
    _put(ws, "toy-store-search.json", _sample())
    _put(ws, "copy.json", _sample())  # declares the same id
    entries = _by_file(_list().stdout)
    assert {n: e["status"] for n, e in entries.items()} == {"toy-store-search.json": "broken", "copy.json": "broken"}
    for e in entries.values():
        assert [p["code"] for p in e["problems"]] == ["duplicate_id"] and e["page"] is None
    rendered = rationale.render_workspace(ws, ws / "site")
    assert all(e["status"] == "broken" for e in rendered)
    assert not (ws / "site" / "explainers" / "toy-store-search.html").exists()
    assert "explainers/toy-store-search.html" not in (ws / "site" / "index.html").read_text(encoding="utf-8")


def test_wiki_build_skips_files_with_one_id(built):
    root = built.root
    _put(root, "toy-store-search.json", _current(root))
    _put(root, "copy.json", _current(root))
    result = _wiki_build()
    assert "duplicate" in result.output.lower() or "broken" in result.output
    assert not (root / PAGE).exists() and PAGE not in _manifest(root)


def test_rationale_build_refuses_an_id_another_file_declares(ws, tmp_path):
    _put(ws, "other.json", _sample())
    result = _invoke("rationale", "build", str(_file(tmp_path, _sample())))
    assert result.exit_code == 2 and "other.json" in json.loads(result.stdout)["error"]
    assert not (ws / "rationale" / "toy-store-search.json").exists()
    assert not (ws / "site" / "explainers").exists()


def test_a_render_error_marks_that_file_broken_and_the_others_render(ws, monkeypatch):
    _put(ws, "toy-store-search.json", _sample())
    _put(ws, "toy-store-explain.json", _explain())
    real = explainer.write_page

    def flaky(doc, *args, **kwargs):
        if doc["id"] == "toy-store-explain":
            raise RuntimeError("template exploded")
        return real(doc, *args, **kwargs)

    monkeypatch.setattr(explainer, "write_page", flaky)
    entries = {e["id"]: e for e in rationale.render_workspace(ws, ws / "site")}
    assert entries["toy-store-search"]["status"] == "ok" and Path(entries["toy-store-search"]["page"]).is_file()
    bad = entries["toy-store-explain"]
    assert bad["status"] == "broken" and bad["page"] is None
    assert bad["problems"][-1]["code"] == "render_failed" and "template exploded" in bad["problems"][-1]["message"]
    index = (ws / "site" / "index.html").read_text(encoding="utf-8")
    assert "explainers/toy-store-search.html" in index and "explainers/toy-store-explain.html" not in index


def test_out_outside_the_current_folder_exits_2_and_writes_nothing(tmp_path, monkeypatch):
    here = tmp_path / "here"
    here.mkdir()
    monkeypatch.chdir(here)
    for out in (tmp_path / "elsewhere", here / ".." / "sneaky"):
        result = _invoke("rationale", "build", str(_file(tmp_path, _zero())), "--out", str(out))
        assert result.exit_code == 2 and "error" in json.loads(result.stdout)
        assert not out.exists()


def test_out_refuses_an_assets_folder_ddspace_did_not_create(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "out"
    (out / "assets").mkdir(parents=True)
    (out / "assets" / "style.css").write_text("mine", encoding="utf-8")
    result = _invoke("rationale", "build", str(_file(tmp_path, _zero())), "--out", str(out))
    assert result.exit_code == 2 and "assets" in json.loads(result.stdout)["error"]
    assert (out / "assets" / "style.css").read_text(encoding="utf-8") == "mine"
    assert not (out / "explainers").exists()


def test_out_writes_a_marker_and_can_build_into_its_own_folder_again(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "out"
    for _ in range(2):
        _built(_invoke("rationale", "build", str(_file(tmp_path, _zero())), "--out", "out"))
    assert (out / "assets" / explainer.ASSETS_MARKER).is_file()
    assert (out / "explainers" / "toy-store-search.html").is_file()


@pytest.mark.parametrize("rid", ["../evil", "a/b", "toy\n"])
def test_an_unsafe_id_exits_2_and_writes_nothing(ws, tmp_path, rid):
    before = (ws / "raw" / "exported.json").read_text(encoding="utf-8")
    doc = _sample()
    doc["id"] = rid
    result = _invoke("rationale", "build", str(_file(tmp_path, doc)))
    assert result.exit_code == 2 and "error" in json.loads(result.stdout)
    assert not (ws / "rationale").exists() and not (ws / "site" / "explainers").exists()
    assert not (ws / "site" / "evil.html").exists() and not (ws / "evil.html").exists()
    assert (ws / "raw" / "exported.json").read_text(encoding="utf-8") == before


@pytest.mark.parametrize("rid", ["../evil", "a/b", "toy\n"])
def test_an_unsafe_id_in_rationale_is_broken_and_not_rendered(ws, rid):
    doc = _sample()
    doc["id"] = rid
    _put(ws, "evil.json", doc)
    [entry] = json.loads(_list().stdout)
    assert entry["status"] == "broken" and any(p["path"] == "/id" for p in entry["problems"])
    [rendered] = rationale.render_workspace(ws, ws / "site")
    assert rendered["status"] == "broken" and rendered["page"] is None
    assert not (ws / "site" / "evil.html").exists() and not (ws / "site" / "explainers").exists()


def test_build_with_a_graph_outside_a_workspace_and_no_out_exits_2(tmp_path, monkeypatch):
    export = tmp_path / "export"
    _wiki(export)
    monkeypatch.chdir(tmp_path)
    result = _invoke("rationale", "build", str(_file(tmp_path, _sample())), "--graph", str(export))
    assert result.exit_code == 2 and "error" in json.loads(result.stdout)
    assert not (export / "rationale").exists() and not (export / "site" / "explainers").exists()


def test_list_from_a_folder_that_is_not_a_workspace_exits_2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = _invoke("rationale", "list")
    assert result.exit_code == 2 and "error" in json.loads(result.stdout)


def test_list_takes_a_graph_like_check_and_build(ws, tmp_path, monkeypatch):
    _put(ws, "toy-store-search.json", _sample())
    monkeypatch.chdir(tmp_path)
    for graph in (ws, ws / "raw" / "graph.json"):
        result = _invoke("rationale", "list", "--graph", str(graph))
        assert result.exit_code == 0, result.output
        assert [(e["id"], e["status"]) for e in json.loads(result.stdout)] == [("toy-store-search", "ok")]


def test_a_space_file_without_a_graph_is_broken_with_no_graph(tmp_path, monkeypatch):
    root = tmp_path / "bare"
    assert _invoke("init", str(root), "--yes").exit_code == 0
    monkeypatch.chdir(root)
    _put(root, "toy-store-search.json", _sample())
    [entry] = json.loads(_list().stdout)
    assert entry["status"] == "broken" and [p["code"] for p in entry["problems"]] == ["no_graph"]


def test_null_free_text_renders_as_nothing(ws):
    from taxonomy_generator.wiki import query as q
    doc = _sample()
    doc["problem"]["context"] = None
    a1, a2 = doc["alternatives"]
    a1["summary"] = None
    a1["choices"][0]["reason"] = None
    a1["choices"][0]["evidence"][0]["stance"] = None
    a1["relations"][0]["note"] = None
    a1["considered"][0]["reason"] = None
    a2["open"][0]["reason"] = None
    doc["comparison"][0]["note"] = None
    graph = q.load(ws / "raw" / "graph.json")
    data = explainer.page_data(doc, graph, lambda target: None)
    assert data["context"] == "" and data["alternatives"][0]["summary"] == ""
    assert data["alternatives"][0]["choices"][0]["evidence"][0]["stance"] == ""
    assert data["alternatives"][1]["open"][0]["reason"] == ""
    html = explainer._render(data)
    visible = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    assert "None" not in visible and "null" not in visible


def test_build_into_a_wiki_exported_before_the_layout_script_adds_it(ws, tmp_path):
    """A wiki exported before graph-layout.js existed: the page still draws its graph without a re-export."""
    layout = ws / "site" / "assets" / "graph-layout.js"
    layout.unlink()
    style = ws / "site" / "assets" / "style.css"
    style.write_text("/* the export's own stylesheet */", encoding="utf-8")
    _built(_invoke("rationale", "build", str(_file(tmp_path, _search_with_a_shared_dimension()))))
    assert layout.is_file()
    assert style.read_text(encoding="utf-8") == "/* the export's own stylesheet */"  # other assets left to the export
    layout.write_text("// an older layout script", encoding="utf-8")  # exported before the current version
    _built(_invoke("rationale", "build", str(_file(tmp_path, _search_with_a_shared_dimension()))))
    assert layout.read_bytes() == explainer.LAYOUT_SCRIPT.read_bytes()


def test_build_into_a_wiki_exported_before_the_explainers_region_lists_the_page(ws, tmp_path):
    """An index exported before the Explainers region existed: the region is added and the page listed once."""
    index = ws / "site" / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace("<!-- explainers --><!-- /explainers -->", ""),
                     encoding="utf-8")
    doc = _search_with_a_shared_dimension()
    for _ in range(2):  # a second build replaces the region it added, it does not add another
        _built(_invoke("rationale", "build", str(_file(tmp_path, doc))))
    text = index.read_text(encoding="utf-8")
    assert text.count("<!-- explainers -->") == 1
    assert text.count(f'href="explainers/{doc["id"]}.html"') == 1
    assert text.index("<!-- explainers -->") < text.index("<footer>")


# ---------------------------------------------------------------- the trajectory on the page


def _data(doc, root):
    from taxonomy_generator.wiki import explainer
    from taxonomy_generator.wiki import query as q

    from delvedspace import rationale

    graph = q.load(root / "raw" / "graph.json") if rationale.names_space(doc) else None
    return explainer.page_data(doc, graph, explainer.wiki_links(None, root))


def test_search_trajectory_marks_what_each_step_changed_and_what_was_proposed(ws):
    data = _data(_sample(), ws)
    steps = data["trajectory"]
    assert [s["move"] for s in steps] == ["seed", "exploit", "explore"]
    assert steps[0]["point"] == {"d:1": "v:1.1", "d:2": "v:2.1"} and steps[0]["alternative"] == "A1"
    assert steps[1]["changed"] == ["d:2"]                      # the exploit step dropped the commit protocol
    assert steps[2]["novel"] == ["d:1"] and steps[2]["alternative"] == "A2"  # WAL in S3: never seen before
    assert steps[0]["description"] and steps[0]["attested_by"][0]["id"] == "s:s1"
    assert data["trajectory_dimensions"] == ["d:1", "d:2"]
    assert data["budget"] == {"max_points": 12, "used": 3}
    assert data["values"]["v:1.1"]["steps"] == [1, 2]
    assert data["alternatives"][0]["point"] == steps[0]["description"]  # the alternative shows its step's point


def test_explain_page_shows_the_regions_as_bands(ws, tmp_path):
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _explain()))))
    html = Path(payload["page"]).read_text(encoding="utf-8")
    assert "Regions that justify the solution" in html and 'class="band-h"' in html
    assert html.count('<td class="band"') == 2 and html.count('<td class="band" title="Disk quorum"><span>') == 1
    data = _data(_explain(), ws)
    assert data["regions"][0]["point"] == {"d:1": "v:1.1"} and data["trajectory"][0]["alternative"] == "S"


def test_zero_shot_trajectory_uses_the_agents_own_names(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, _zero())), "--out", "out"))
    html = Path(payload["page"]).read_text(encoding="utf-8")
    visible = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    assert 'data-panel="trajectory"' in html and "Local disks" in html and "Attested by" not in visible
    data = _data(_zero(), tmp_path)
    assert [s["point"] for s in data["trajectory"]] == [{"z:1": "z:1.1"}, {"z:1": "z:1.2"}]   # short ids, no text
    assert data["dimensions"]["z:1"]["label"] == "Store" and not data["wiki"]
    assert data["values"]["z:1.3"]["label"] == "Postgres"   # a value the agent named that no step took
    assert [s["approach"] for s in data["trajectory"]] == ["A", "B"] and data["approaches"][1]["idea"]
    assert data["relations"] == [{"source": "z:1", "target": "z:2", "type": "constrains", "directed": True,
                                  "reading": ""}]   # the relation the alternatives claim
    assert "No space was provided" in visible and "the agent named" in html



def test_the_adrs_tab_lists_requirements_no_adr_or_decision_addresses(ws):
    doc = _sample()
    doc["problem"]["requirements"].append({"id": "Q9", "kind": "quality", "text": "Nobody addresses this."})
    data = _data(doc, ws)
    assert [(u["id"], u["reason"], u["reason_text"]) for u in data["unaddressed"]] == [("Q9", "", "no reason given")]
    assert [a["id"] for a in data["adrs"]] == ["ADR1", "ADR2"]
    assert data["adrs"][0]["options"][0]["point"] == {"d:1": "v:1.1"} and data["adrs"][0]["options"][0]["key"] == "ADR1:O1"
    a1, a2 = data["alternatives"]   # each alternative is composed of the partial points its ADRs choose for it
    assert [(p["adr"], p["option"], p["point"]) for p in a1["parts"]] == [("ADR1", "O1", {"d:1": "v:1.1"}),
                                                                          ("ADR2", "O1", {"d:2": "v:2.1"})]
    assert [(p["adr"], p["option"]) for p in a2["parts"]] == [("ADR1", "O2")]
    html = explainer._render(data)
    assert "Requirements not addressed" in html and 'data-requirement="Q9"' in html
    clean = explainer._render(_data(_sample(), ws))
    assert "Every requirement is addressed" in clean and "No gaps:" in clean



def test_search_trajectory_has_lanes_a_requirement_strip_and_a_story(ws):
    data = _data(_sample(), ws)
    lanes = data["lanes"]
    assert lanes["rounds"] == [1, 2]
    assert [(l["approach"], l["alternative"]) for l in lanes["lanes"]] == [("A", "A1"), ("B", "A2")]
    assert [c["step"] for c in lanes["lanes"][0]["cells"][1]] == [1] and [c["step"] for c in lanes["lanes"][0]["cells"][2]] == [2]
    steps = data["trajectory"]
    assert steps[1]["diff"] == [{"dimension": "d:2", "before": "v:2.1", "after": None}]  # step 2 dropped the commit protocol
    html = explainer._render(data)
    assert 'class="lanes"' in html and html.count('<button type="button" class="node-chip') == 3
    assert 'class="heat"' in html and 'class="h h-meets' in html and html.count('class="story-step') == 3
    assert "Round 2</b> · 2 points: refine A, new approach B" in html
    assert "drop" in html and 'class="qoc' not in html


def test_explain_trajectory_has_a_story_and_questions_options_criteria(ws):
    doc = _explain()
    doc["trajectory"].append({"step": 3, "move": "contrast", "parent": 2, "values": ["v:1.2"], "hypothesis": "h",
                              "assessment": {"Q1": "misses"}, "tradeoffs": [], "observation": "o", "verdict": "ungrounded"})
    data = _data(doc, ws)
    assert data["lanes"] is None
    (q1, q2) = data["qoc"]
    assert q1["dimension"] == "d:1" and [(o["value"], o["kind"], o["step"], o["specific"]) for o in q1["options"]] == [
        ("v:1.1", "solution", 2, True), ("v:1.2", "contrast", 3, True)]
    assert q1["options"][0]["forced"] is True and q2["options"][0]["specific"] is False   # d:2 only within the whole
    html = explainer._render(data)
    assert 'class="qoc-wrap"' in html and 'data-qoc="0:1"' in html and 'data-crit="Q1"' in html
    assert "the solution · forced" in html and "judged only within the whole solution" in html
    assert 'class="lanes"' not in html and 'class="heat"' not in html



def test_a_reused_point_says_so_on_the_page(ws):
    from tests.unit_tests.test_rationale_build import _search_with_a_shared_dimension
    data = _data(_search_with_a_shared_dimension(), ws)   # step 3 names P2, which step 2 evaluated
    assert [(s["point_id"], s["reuses"]) for s in data["trajectory"]] == [("P1", None), ("P2", None), ("P2", 2)]
    assert "same point as #2, reused" in explainer._render(data)


def test_the_gaps_section_at_the_bottom_lists_reasons_nearest_dimensions_and_approximate_fits(ws):
    doc = _sample()
    doc["problem"]["requirements"].append({"id": "Q9", "kind": "quality", "text": "Audit every read."})
    doc["unaddressed"] = [{"requirement": "Q9", "reason": "no_dimension", "nearest_dimension_id": "d:1",
                           "note": "The space has no dimension for auditing."}]
    doc["adrs"][0]["options"][0].update(fit="approximate", fit_note="Disk quorum stands in for any local store.")
    data = _data(doc, ws)
    [u] = data["unaddressed"]
    assert (u["id"], u["reason_text"], u["nearest"]["label"]) == ("Q9", "the space has no dimension for it",
                                                                  "Source of truth")
    assert [(f["where"], f["option"], f["point"]) for f in data["fits"]] == [
        ("ADR1 · " + doc["adrs"][0]["options"][0]["name"], "ADR1:O1", {"d:1": "v:1.1"})]
    html = explainer._render(data)
    main = html[:html.index("</main>")]
    assert main.rindex('id="gaps"') > main.rindex('data-panel=')   # below every tab
    assert "1</strong> requirement not addressed (1 with no dimension)" in html
    assert 'data-gap-option="ADR1:O1"' in html and "approximate fit" in html
    assert "The space has no dimension for auditing." in html


def test_an_approximate_option_lists_only_the_values_its_choices_mark_approximate(ws):
    doc = _sample()
    doc["adrs"][0]["options"][0].update(values=["v:1.1", "v:2.1"], fit="approximate", fit_note="n")
    assert _data(doc, ws)["fits"][0]["point"] == {"d:1": "v:1.1", "d:2": "v:2.1"}   # no choice marked: all
    doc["alternatives"][0]["choices"][1].update(fit="approximate", fit_note="n")   # A1's v:2.1
    fits = _data(doc, ws)["fits"]
    assert [(f["option"], f["point"]) for f in fits] == [("ADR1:O1", {"d:2": "v:2.1"})]   # the choice is not listed twice


def test_a_step_shows_its_trade_offs_and_the_points_own_trade_off(ws, tmp_path):
    doc = _sample()
    doc["points"][0]["description"] = "Disks with a quorum. Trade-off: durable, at the cost of write latency."
    payload = _built(_invoke("rationale", "build", str(_file(tmp_path, doc))))
    html = Path(payload["page"]).read_text(encoding="utf-8")
    assert '<ul class="tradeoffs">' in html and '<span class="t-cost">gives up</span>' in html
    assert re.search(r'<ul class="tradeoffs"><li>[^\n]*?Three-phase commit[^\n]*?: <span class="t-gain">', html)  # its cause
    assert "Serves requests durably, but the commit protocol adds cost." in html     # the fixture's note
    assert "The point's trade-off</span> durable, at the cost of write latency." in html
    assert "Disks with a quorum.</p>" in html                                       # the description, split


def test_split_tradeoff():
    assert explainer.split_tradeoff("A. Trade-off: B.") == ("A.", "B.")
    assert explainer.split_tradeoff("No mark here.") == ("No mark here.", "")


def test_explain_with_inferred_requirements_says_so(ws, tmp_path):
    doc = _explain()
    doc["problem"]["inferred"] = True
    _built(_invoke("rationale", "build", str(_file(tmp_path, doc))))
    html = (ws / "site" / "explainers" / "toy-store-explain.html").read_text(encoding="utf-8")
    assert "Requirements (inferred from the solution)" in html and "the agent inferred these requirements" in html
    plain = _explain()
    _built(_invoke("rationale", "build", str(_file(tmp_path, plain, "plain.json"))))
    assert "inferred from the solution" not in (ws / "site" / "explainers" / "toy-store-explain.html").read_text()
