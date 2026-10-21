"""Agent access to an exported design space: raw/graph.json, raw/tree.json and the query functions."""

import json

import pytest

from taxonomy_generator.wiki import build, write
from taxonomy_generator.wiki import query as q
from tests.unit_tests.test_wiki_export import CORPUS, POINTS, _inputs


@pytest.fixture
def export_dir(tmp_path):
    write(build(_inputs(design_points=POINTS)), tmp_path / "x", "toy")
    return tmp_path / "x"


@pytest.fixture
def graph(export_dir):
    return q.load(export_dir / "raw" / "graph.json")


# ---------------------------------------------------------------- raw files (WA1)


def test_export_writes_graph_and_tree_json_with_identity(export_dir):
    g = json.loads((export_dir / "raw" / "graph.json").read_text())
    t = json.loads((export_dir / "raw" / "tree.json").read_text())
    for data in (g, t):
        assert data["schema_version"] == q.SCHEMA_VERSION
        assert data["run"] == "20261008_000000" and data["view"] == "selected"
        assert data["core_rule"].startswith("≥ 2 sources")
    assert {n["kind"] for n in g["nodes"]} >= {"dimension", "value", "source", "system", "design"}
    assert t["children"] and t["children"][0]["kind"] == "dimension"


def test_raw_files_are_deterministic(tmp_path):
    for name in ("a", "b"):
        write(build(_inputs(design_points=POINTS)), tmp_path / name, "toy")
    for f in ("graph.json", "tree.json"):
        assert (tmp_path / "a" / "raw" / f).read_bytes() == (tmp_path / "b" / "raw" / f).read_bytes()


def test_value_nodes_cite_passages_with_stance_and_hrefs_exist(export_dir, graph):
    wal = q.node(graph, "v:1.2")
    assert wal["passages"] == [{"doc": "s01_p02", "stance": "rejects"}, {"doc": "s02_p01", "stance": "accepts"}]
    assert wal["dimension_id"] == "d:1"
    for n in graph["nodes"]:
        assert (export_dir / "wiki" / f"{n['href']}.md").is_file(), n["href"]
        assert (export_dir / "html" / f"{n['href']}.html").is_file(), n["href"]


def test_graph_json_never_contains_passage_text(export_dir):
    text = (export_dir / "raw" / "graph.json").read_text() + (export_dir / "raw" / "tree.json").read_text()
    for passage in CORPUS.values():
        assert passage["content"] not in text


# ---------------------------------------------------------------- resolving nodes


@pytest.mark.parametrize("ref, expected", [
    ("d:1", "d:1"), ("concepts/source-of-truth", "d:1"), ("source-of-truth", "d:1"),
    ("Source of truth", "d:1"), ("source OF truth", "d:1"), ("WAL in S3", "v:1.2"), ("s01", "s:s1"), ("s1", "s:s1"), ("s:s1", "s:s1"),
])
def test_resolve_by_id_slug_or_label(graph, ref, expected):
    assert q.resolve(graph, ref)["id"] == expected


def test_resolve_ambiguous_label_lists_candidates(graph):
    with pytest.raises(q.NotFound) as err:
        q.resolve(graph, "Shared label")
    assert {c["id"] for c in err.value.candidates} == {"v:1.3", "v:2.2"}


def test_resolve_unknown_suggests_close_matches(graph):
    with pytest.raises(q.NotFound) as err:
        q.resolve(graph, "Replicaton", kinds=("dimension",))
    assert [c["label"] for c in err.value.candidates] == ["Replication"]


def test_resolve_partial_label_when_unique(graph):
    assert q.resolve(graph, "three-phase")["id"] == "v:2.1"


# ---------------------------------------------------------------- commands (WA2)


def test_info(graph, export_dir):
    info = q.info(graph)
    assert info["run"] == "20261008_000000"
    assert info["counts"]["dimensions"] == 2 and info["counts"]["values"] == 6 and info["counts"]["relations"] == 1


def test_dims_lists_counts_and_core_flag(graph):
    dims = {d["label"]: d for d in q.dims(graph)}
    assert dims["Source of truth"]["values"] == 3 and dims["Source of truth"]["core"] is True
    assert dims["Source of truth"]["evidence"] == {"codes": 5, "documents": 3, "sources": 2}
    assert [d["label"] for d in q.dims(graph, core_only=True)] == [d["label"] for d in q.dims(graph) if d["core"]]


def test_values_of_a_dimension_filtered_by_stance(graph):
    out = q.values(graph, "Source of truth")
    assert out["dimension"]["id"] == "d:1" and [v["label"] for v in out["values"]] == ["Disk quorum", "WAL in S3",
                                                                                        "Shared label"]
    assert [v["label"] for v in q.values(graph, "Source of truth", status="mixed")["values"]] == ["WAL in S3"]
    with pytest.raises(q.NotFound):
        q.values(graph, "WAL in S3")  # a value is not a dimension


def test_evidence_groups_passages_by_source(graph):
    out = q.evidence(graph, "WAL in S3")
    assert out["value"]["status"] == "mixed" and out["value"]["dimension"] == "Source of truth"
    by_source = {s["id"]: s for s in out["sources"]}
    assert by_source["s:s1"]["passages"] == [{"id": "s01_p02", "stance": "rejects"}]
    only = q.evidence(graph, "WAL in S3", stance="accepts")
    assert [p["id"] for s in only["sources"] for p in s["passages"]] == ["s02_p01"]


def test_evidence_with_quotes_reads_the_corpus(graph):
    out = q.evidence(graph, "WAL in S3", corpus=CORPUS)
    texts = {p["id"]: p["text"] for s in out["sources"] for p in s["passages"]}
    assert texts["s02_p01"] == "Continuity writes a WAL to S3."


def test_show_lists_fields_and_neighbors_by_edge_type(graph):
    out = q.show(graph, "Source of truth")
    assert out["node"]["kind"] == "dimension"
    assert {n["id"] for n in out["neighbors"]["has_value"]} == {"v:1.1", "v:1.2", "v:1.3"}
    rel = out["neighbors"]["relation"][0]
    assert rel["id"] == "d:2" and rel["direction"] == "out" and rel["relation"] == "constrains"
    assert "Source of truth" in rel["reading"]


def test_relations_filtered_by_dimension_and_type(graph):
    assert [r["type"] for r in q.relations(graph)] == ["constrains"]
    assert q.relations(graph, frm="Replication") == []          # only outgoing for directed types
    assert len(q.relations(graph, frm="Source of truth", rtype="constrains")) == 1
    assert q.relations(graph, rtype="requires") == []


def test_search_matches_labels_then_descriptions(graph):
    hits = q.search(graph, "replica")
    assert hits[0]["id"] == "d:2" and hits[0]["match"] == "label"
    assert all(h["kind"] == "value" for h in q.search(graph, "description", kind="value"))


def test_old_exports_without_raw_files_explain_how_to_get_them(tmp_path):
    with pytest.raises(q.QueryError, match="re-export"):
        q.load(tmp_path / "raw" / "graph.json")

