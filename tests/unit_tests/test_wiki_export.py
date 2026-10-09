"""taxonomy_generator.wiki: design-space wiki export (markdown, HTML pages, graph page)."""

import csv
import importlib.util
import json
import re
from pathlib import Path

from taxonomy_generator.wiki import Inputs, build, write
from taxonomy_generator.wiki.model import excerpt, slugify

_spec = importlib.util.spec_from_file_location(
    "export_wiki_cli", Path(__file__).resolve().parents[2] / "benchmark" / "export_wiki.py")
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


def _value(vid, label, status, docs, accepted=(), rejected=()):
    return {"id": vid, "label": label, "description": f"{label} description.", "status": status,
            "supporting_doc_ids": list(docs), "stances": {"accepted": list(accepted), "rejected": list(rejected)}}


def _taxonomy():
    dims = [
        {"id": "1", "name": "Source of truth", "description": "Where does the truth live?",
         "relations": [{"target_id": "2", "type": "constrains", "rationale": "Truth shapes replication."}],
         "evidence": {"codes": 5, "documents": 3, "sources": 2},
         "values": [_value("1.1", "Disk quorum", "accepted", ["s01_p01"], accepted=["s01_p01"]),
                    _value("1.2", "WAL in S3", "mixed", ["s02_p01", "s01_p02"], accepted=["s02_p01"], rejected=["s01_p02"]),
                    _value("1.3", "Shared label", "rejected", ["s01_p02"], rejected=["s01_p02"])]},
        {"id": "2", "name": "Replication", "description": "How are replicas kept in sync?", "relations": [],
         "evidence": {"codes": 4, "documents": 2, "sources": 2},
         "values": [_value("2.1", "Three-phase commit", "accepted", ["s01_p01"]),
                    _value("2.2", "Shared label", "accepted", ["s02_p01"]),
                    _value("2.3", "Lower latency", "outcome", ["s02_p01"])]},
    ]
    return {"taxonomy_name": "toy", "selected_clusters": dims,
            "iterations": [{"clusters": dims + [{"id": "9", "name": "Dropped topic", "values": []}]}],
            "dropped_dimensions": [{"id": "9", "rationale": "Not a decision point."}],
            "run_metrics": {"total_tokens": 1000}}


CORPUS = {
    "s01_p01": {"id": "s01_p01", "content": "## Heading line\nSpokes keeps *three* copies [always].", "section": "Spokes"},
    "s01_p02": {"id": "s01_p02", "content": "Filesystems were rejected.", "section": "History"},
    "s02_p01": {"id": "s02_p01", "content": "Continuity writes a WAL to S3.", "section": "Continuity"},
}
SYSTEMS = {"s01_p01": {"systems": ["SPOKES"], "primary": "SPOKES"}, "s01_p02": {"systems": ["FS"], "primary": "FS"},
           "s02_p01": {"systems": ["CONT"], "primary": "CONT"}, "other_doc": {"systems": ["UNUSED"], "primary": "UNUSED"}}
POINTS = {"seed": 42, "samples": [{"k": 2, "groups": {
    "attested": [{"point_id": "P001", "group": "attested", "system": "SPOKES",
                  "values": [{"dimension_id": "1", "dimension": "Source of truth", "value_id": "1.1", "label": "Disk quorum", "status": "accepted"},
                             {"dimension_id": "2", "dimension": "Replication", "value_id": "2.1", "label": "Three-phase commit", "status": "accepted"}],
                  "relations": [{"source": "1", "target": "2", "type": "constrains"}]}],
    "novel": [{"point_id": "P002", "group": "novel",
               "values": [{"dimension_id": "1", "dimension": "Source of truth", "value_id": "1.2", "label": "WAL in S3", "status": "mixed"},
                          {"dimension_id": "2", "dimension": "Replication", "value_id": "2.1", "label": "Three-phase commit", "status": "accepted"}]}],
    "control": []}, "diagnostics": {"note": ""}}]}


def _inputs(**over):
    base = dict(taxonomy=_taxonomy(), taxonomy_name="toy", run_label="20261008_000000", corpus=CORPUS,
                systems=SYSTEMS, use_case="Mine Git hosting decisions.")
    base.update(over)
    return Inputs(**base)


def _tree(root: Path):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_same_inputs_give_identical_output(tmp_path):
    write(build(_inputs(design_points=POINTS)), tmp_path / "a", "toy")
    write(build(_inputs(design_points=POINTS)), tmp_path / "b", "toy")
    assert _tree(tmp_path / "a") == _tree(tmp_path / "b")


def test_every_wikilink_resolves():
    export = build(_inputs(design_points=POINTS))
    paths = {p.path for p in export.pages}
    for page in export.pages:
        text = page.body + json.dumps(page.frontmatter)
        for target in re.findall(r"\[\[([^\]|]+)", text):
            assert target in paths, (page.path, target)


def test_every_html_link_resolves(tmp_path):
    write(build(_inputs(design_points=POINTS)), tmp_path, "toy")
    html_root = tmp_path / "html"
    files = list(html_root.rglob("*.html"))
    assert (html_root / "graph.html") in files and (html_root / "assets" / "d3.min.js").exists()
    for f in files:
        markup = re.sub(r"<script>.*?</script>", "", f.read_text(encoding="utf-8"), flags=re.S)  # runtime-built links
        for href in re.findall(r'(?:href|src)="([^"#]+)', markup):
            if href.startswith(("http:", "https:", "mailto:")):
                continue
            assert (f.parent / href).resolve().exists(), (f, href)


def test_without_design_points_nothing_refers_to_them(tmp_path):
    export = build(_inputs())
    assert not any(p.path.startswith("designs/") or p.path == "synthesis/design-points" for p in export.pages)
    assert not any(n["kind"] == "design" for n in export.graph["nodes"])
    write(export, tmp_path, "toy")
    assert not (tmp_path / "wiki" / "designs").exists()
    text = "".join(re.sub(r"<script>.*?</script>", "", p.read_text(encoding="utf-8"), flags=re.S)
                   for p in (tmp_path / "html").rglob("*.html"))
    assert "designs/" not in text and "design-points.html" not in text
    assert '<input type="checkbox" data-kind="design"' not in text and 'id="design-filters"' not in text


def test_with_design_points_pages_and_graph_layer_exist():
    export = build(_inputs(design_points=POINTS))
    paths = {p.path for p in export.pages}
    assert {"designs/p001", "designs/p002", "synthesis/design-points"} <= paths
    design_edges = [e for e in export.graph["edges"] if e["type"] == "design"]
    assert {(e["source"], e["target"]) for e in design_edges} == {("p:P001", "v:1.1"), ("p:P001", "v:2.1"),
                                                                 ("p:P002", "v:1.2"), ("p:P002", "v:2.1")}
    value = next(p for p in export.pages if p.path == "entities/disk-quorum")
    assert value.frontmatter["design_points"] == ["[[designs/p001|P001]]"]


def test_no_quotes_removes_passage_text():
    with_q = next(p for p in build(_inputs()).pages if p.path == "entities/disk-quorum")
    without = next(p for p in build(_inputs(quotes=False)).pages if p.path == "entities/disk-quorum")
    assert "Spokes keeps" in with_q.body and "s01_p01" in with_q.body
    assert "Spokes keeps" not in without.body and "s01_p01" in without.body


def test_duplicate_labels_get_distinct_pages():
    paths = [p.path for p in build(_inputs()).pages if p.kind == "value"]
    assert len(paths) == len(set(paths)) == 6
    assert {"entities/shared-label", "entities/shared-label-2"} <= set(paths)


def test_excerpt_skips_headings_and_escapes_markdown():
    text = excerpt(CORPUS["s01_p01"]["content"], 60)
    assert "Heading" not in text and text.startswith("Spokes keeps \\*three\\* copies \\[always\\]")
    assert slugify("Write-ahead log (WAL) in S3!") == "write-ahead-log-wal-in-s3"


def test_system_pages_only_for_systems_with_evidence_in_the_run():
    export = build(_inputs())
    systems = {p.path for p in export.pages if p.kind == "system"}
    assert systems == {"synthesis/systems/cont", "synthesis/systems/fs", "synthesis/systems/spokes"}
    matrix = next(p for p in export.pages if p.path == "synthesis/system-matrix")
    assert "Disk quorum" in matrix.body


def test_mixed_stance_and_relations_in_graph():
    export = build(_inputs())
    edges = {(e["source"], e["target"], e.get("stance"), e.get("relation")) for e in export.graph["edges"]}
    assert ("d:1", "d:2", None, "constrains") in edges
    assert ("s:s2", "v:1.2", "accepts", None) in edges and ("s:s1", "v:1.2", "rejects", None) in edges


def test_cli_writes_the_export(tmp_path):
    run = tmp_path / "toy_taxonomy_20261008_000000.json"
    run.write_text(json.dumps(_taxonomy()), encoding="utf-8")
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps(list(CORPUS.values())), encoding="utf-8")
    sources = tmp_path / "sources.csv"
    with open(sources, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "url", "source_type"])
        w.writerow(["s1", "Spokes post", "https://example.org/spokes", "blog"])
        w.writerow(["s2", "Cursor post", "https://example.org/cursor", "blog"])
    dp = tmp_path / "points.json"
    dp.write_text(json.dumps(POINTS), encoding="utf-8")
    assert cli.main([str(run), "--corpus", str(corpus), "--sources", str(sources), "--design-points", str(dp)]) == 0
    out = tmp_path / "toy_taxonomy_20261008_000000_wiki"
    assert (out / ".llmwiki.yaml").exists() and (out / "SCHEMA.md").exists()
    assert (out / "wiki" / "sources" / "s1.md").read_text(encoding="utf-8").startswith("---\ntitle: Spokes post")
    manifest = json.loads((out / "raw" / "run.json").read_text(encoding="utf-8"))
    assert manifest["quotes"] is True and manifest["pages"] > 10
    assert (out / "html" / "designs" / "p001.html").exists()


def _with_evaluation(tax):
    crit = [{"name": "Orthogonality", "description": "Distinct decision points.", "threshold": 0.5,
             "evaluated": True, "score": 0.7, "passed": True, "reason": "Mostly distinct | one overlap."},
            {"name": "Clarity", "description": "Clear names.", "threshold": 0.5, "evaluated": True,
             "score": 0.4, "passed": False, "reason": "Some names are vague."}]
    tax["evaluation"] = {"criteria": crit, "overall": 0.55, "model": "openai/judge", "view": "final", "dimensions": 2}
    tax["evaluation_history"] = [{"criteria": crit, "overall": 0.5, "view": "draft", "iteration": 1, "dimensions": 3},
                                 {"criteria": crit, "overall": 0.55, "view": "final", "iteration": "final", "dimensions": 2}]
    return tax


def test_overview_has_use_case_narrative_run_summary_and_list_cells(tmp_path):
    export = build(_inputs(narrative="Delve found **two** decisions.", taxonomy=_with_evaluation(_taxonomy())))
    overview = next(p for p in export.pages if p.path == "synthesis/overview")
    assert "## Use case" in overview.body and "Mine Git hosting decisions." in overview.body
    assert "Delve found **two** decisions." in overview.body
    assert "| Values | 6: 3 accepted, 1 mixed, 1 rejected, 1 outcome |" in overview.body
    assert "Evaluation score | 0.55" in overview.body
    write(export, tmp_path, "toy")
    html = (tmp_path / "html" / "synthesis" / "overview.html").read_text(encoding="utf-8")
    assert '<ul class="cell-list"><li><a href="../entities/disk-quorum.html">Disk quorum</a></li>' in html
    assert "<strong>two</strong>" in html and "&lt;br&gt;" not in html


def test_evaluation_page_is_optional():
    tax = _with_evaluation(_taxonomy())
    assert not any(p.path == "synthesis/evaluation" for p in build(_inputs(taxonomy=tax)).pages)
    export = build(_inputs(taxonomy=tax, evaluation=True))
    page = next(p for p in export.pages if p.path == "synthesis/evaluation")
    assert "Overall score **0.55**" in page.body and "Mostly distinct \\| one overlap." in page.body
    assert "## Across iterations" in page.body and "| draft | 3 | 0.50 | 0.7 | 0.4 |" in page.body
    index = next(p for p in export.pages if p.path == "index")
    assert "[[synthesis/evaluation|Evaluation]]" in index.body
    # requested but no evaluation in the run: no page, no link
    plain = build(_inputs(evaluation=True))
    assert not any(p.path == "synthesis/evaluation" for p in plain.pages)
    assert "synthesis/evaluation" not in next(p for p in plain.pages if p.path == "index").body


def test_cli_uses_only_the_report_of_the_same_run(tmp_path):
    run = tmp_path / "toy_taxonomy_20261008_000000.json"
    run.write_text(json.dumps(_taxonomy()), encoding="utf-8")
    (tmp_path / "toy_report_20261001_000000.md").write_text("## Narrative Summary\n\nOld run.\n", encoding="utf-8")
    assert cli.main([str(run)]) == 0
    out = tmp_path / "toy_taxonomy_20261008_000000_wiki"
    assert "Old run." not in (out / "wiki" / "synthesis" / "overview.md").read_text(encoding="utf-8")
    (tmp_path / "toy_report_20261008_000000.md").write_text("## Narrative Summary\n\nThis run.\n\n## Other\n", encoding="utf-8")
    assert cli.main([str(run)]) == 0
    text = (out / "wiki" / "synthesis" / "overview.md").read_text(encoding="utf-8")
    assert "This run." in text and "Old run." not in text


def test_sidebar_follows_the_index_order(tmp_path):
    export = build(_inputs(design_points=POINTS, taxonomy=_with_evaluation(_taxonomy()), evaluation=True))
    write(export, tmp_path, "toy")
    html = (tmp_path / "html" / "index.html").read_text(encoding="utf-8")
    sidebar = html[html.index('<aside class="sidebar">'):html.index("</aside>")]
    groups = re.findall(r"<summary>([A-Za-z ]+) \(", sidebar)
    assert groups == ["Dimensions", "Values", "Synthesis", "Systems", "Sources", "Design points"]
    synth = sidebar[sidebar.index("<summary>Synthesis"):sidebar.index("<summary>Systems")]
    titles = re.findall(r'href="synthesis/[^"]+">([^<]+)</a>', synth)
    assert titles == ["Overview", "Contested decisions", "Dropped and unsupported", "System × dimension matrix",
                      "Design points", "Evaluation"]


def test_index_explains_sections_and_names_llms_but_not_tokens():
    models = {"generation_llm": "openai/gen", "evaluation_llm": "openai/judge", "embedding": "openai/emb"}
    export = build(_inputs(models=models))
    index = next(p for p in export.pages if p.path == "index")
    assert "A dimension is one design decision" in index.body and "**mixed**" in index.body
    assert "*The documents the design space was mined from." in index.body
    assert index.frontmatter["generation_llm"] == "openai/gen" and "total_tokens" not in index.frontmatter
    overview = next(p for p in export.pages if p.path == "synthesis/overview")
    assert "| Generation LLM | `openai/gen` |" in overview.body and "| Evaluation LLM (judge) | `openai/judge` |" in overview.body
    assert "Tokens" not in overview.body and "1000" not in overview.body


def test_logo_and_case_icon(tmp_path):
    icon = tmp_path / "icon.svg"
    icon.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
    write(build(_inputs(case_icon=True)), tmp_path / "with", "toy", icon)
    assets = tmp_path / "with" / "html" / "assets"
    assert {"delvedspace-logo.svg", "delvedspace-icon.svg", "case-icon.svg"} <= {p.name for p in assets.iterdir()}
    assert (tmp_path / "with" / "wiki" / "assets" / "case-icon.svg").exists()
    index = (tmp_path / "with" / "html" / "index.html").read_text(encoding="utf-8")
    assert 'src="assets/delvedspace-logo.svg"' in index and 'src="assets/case-icon.svg"' in index
    value = (tmp_path / "with" / "html" / "entities" / "disk-quorum.html").read_text(encoding="utf-8")
    assert 'href="../assets/delvedspace-icon.svg"' in value
    write(build(_inputs()), tmp_path / "without", "toy")
    assert not (tmp_path / "without" / "html" / "assets" / "case-icon.svg").exists()
    assert "case-icon" not in (tmp_path / "without" / "html" / "index.html").read_text(encoding="utf-8")


def test_exported_images_carry_small_display_sizes(tmp_path):
    icon = tmp_path / "icon.svg"
    icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256"/>', encoding="utf-8")
    write(build(_inputs(case_icon=True)), tmp_path / "out", "toy", icon)
    for folder in ("html", "wiki"):
        assets = tmp_path / "out" / folder / "assets"
        logo = (assets / "delvedspace-logo.svg").read_text(encoding="utf-8")
        case = (assets / "case-icon.svg").read_text(encoding="utf-8")
        root = re.search(r"<svg\b[^>]*>", logo).group(0)
        assert 'width="220" height="64"' in root and 'width="880"' not in root
        assert re.search(r'<svg[^>]*viewBox="0 0 256 256"[^>]*width="32" height="32"/>', case)


def _cli_run(tmp_path):
    run = tmp_path / "toy_taxonomy_20261008_000000.json"
    run.write_text(json.dumps(_taxonomy()), encoding="utf-8")
    sysmap = tmp_path / "map.csv"
    with open(sysmap, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["passage_id", "corpus", "systems", "primary", "basis"])
        for doc, info in SYSTEMS.items():
            w.writerow([doc, "raw", info["primary"], info["primary"], "b"])
    return run, sysmap


def test_cli_can_sample_design_points_at_export(tmp_path):
    from taxonomy_generator.evaluation.design_points import load_system_map, sample_points
    run, sysmap = _cli_run(tmp_path)
    assert cli.main([str(run), "--systems", str(sysmap), "--sample-design-points", "--dp-k", "2", "--dp-n", "3"]) == 0
    out = tmp_path / "toy_taxonomy_20261008_000000_wiki"
    assert (out / "wiki" / "synthesis" / "design-points.md").exists()
    expected = sample_points(_taxonomy()["selected_clusters"], load_system_map(sysmap, "primary"), [2], 3, 42)
    ids = sorted(p["point_id"] for s in expected for g in s["groups"].values() for p in g)
    assert sorted(p.stem.upper() for p in (out / "wiki" / "designs").glob("*.md")) == ids
    manifest = json.loads((out / "raw" / "run.json").read_text(encoding="utf-8"))
    assert manifest["design_points"].startswith("sampled at export (k=2, n=3, seed=42)")


def test_cli_design_points_stay_optional_and_exclusive(tmp_path):
    import pytest
    run, sysmap = _cli_run(tmp_path)
    assert cli.main([str(run), "--systems", str(sysmap)]) == 0
    assert not (tmp_path / "toy_taxonomy_20261008_000000_wiki" / "wiki" / "designs").exists()
    with pytest.raises(SystemExit):
        cli.main([str(run), "--design-points", str(run), "--sample-design-points"])


def test_source_summaries_are_shown_and_labeled(tmp_path):
    summaries = {"s1": "A GitHub post about Spokes. It covers replication.", "s2": "A Cursor article."}
    export = build(_inputs(source_summaries=summaries, summary_model="openai/gen"))
    page = next(p for p in export.pages if p.path == "sources/s1")
    assert "## Summary" in page.body and "It covers replication." in page.body
    assert "generated by `openai/gen` for this wiki; it is not part of the mining." in page.body
    index = next(p for p in export.pages if p.path == "index")
    assert "[[sources/s1|s1]]: A GitHub post about Spokes." in index.body and "It covers replication." not in index.body
    plain = next(p for p in build(_inputs()).pages if p.path == "sources/s1")
    assert "## Summary" not in plain.body


def test_cli_picks_up_source_summaries_next_to_sources(tmp_path):
    run, _ = _cli_run(tmp_path)
    sources = tmp_path / "sources.csv"
    sources.write_text("id,title,url,source_type\ns1,Spokes post,https://example.org,blog\n", encoding="utf-8")
    (tmp_path / "source_summaries.json").write_text(json.dumps(
        {"model": "openai/gen", "summaries": {"s1": {"summary": "Spokes keeps replicas in sync."}}}), encoding="utf-8")
    assert cli.main([str(run), "--sources", str(sources)]) == 0
    md = (tmp_path / "toy_taxonomy_20261008_000000_wiki" / "wiki" / "sources" / "s1.md").read_text(encoding="utf-8")
    assert "Spokes keeps replicas in sync." in md


def test_design_point_descriptions_are_rendered_by_combination():
    from taxonomy_generator.evaluation.design_points import point_signature as sampler_signature
    from taxonomy_generator.wiki.model import point_signature
    p1 = POINTS["samples"][0]["groups"]["attested"][0]
    assert point_signature(p1) == sampler_signature(p1) == "1=1.1|2=2.1"
    export = build(_inputs(design_points=POINTS, point_descriptions={"1=1.1|2=2.1": "A quorum of disk replicas."},
                           point_model="openai/gen"))
    page = next(p for p in export.pages if p.path == "designs/p001")
    assert "## Description" in page.body and "A quorum of disk replicas." in page.body
    assert "without knowing the point's group" in page.body
    other = next(p for p in export.pages if p.path == "designs/p002")
    assert "## Description" not in other.body
    node = next(n for n in export.graph["nodes"] if n["id"] == "p:P001")
    assert node["description"] == "A quorum of disk replicas."


def test_cli_finds_descriptions_next_to_the_design_points(tmp_path):
    run, sysmap = _cli_run(tmp_path)
    dp = tmp_path / "toy_design_points.json"
    dp.write_text(json.dumps(POINTS), encoding="utf-8")
    (tmp_path / "toy_design_points_descriptions.json").write_text(json.dumps(
        {"model": "openai/gen", "descriptions": {"1=1.2|2=2.1": {"point_id": "P002", "description": "A WAL with 3PC."}}}),
        encoding="utf-8")
    assert cli.main([str(run), "--design-points", str(dp)]) == 0
    md = (tmp_path / "toy_taxonomy_20261008_000000_wiki" / "wiki" / "designs" / "p002.md").read_text(encoding="utf-8")
    assert "A WAL with 3PC." in md


def test_graph_nodes_carry_descriptions_and_pages_show_the_case_icon(tmp_path):
    export = build(_inputs(source_summaries={"s1": "A Spokes post."}, case_icon=True))
    nodes = {n["id"]: n for n in export.graph["nodes"]}
    assert nodes["d:1"]["description"] == "Where does the truth live?" and "description_note" not in nodes["d:1"]
    assert nodes["v:1.1"]["description"] == "Disk quorum description."
    assert nodes["s:s1"]["description"] == "A Spokes post." and "Generated" in nodes["s:s1"]["description_note"]
    assert "description" not in nodes["s:s2"]
    icon = tmp_path / "icon.svg"
    icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>', encoding="utf-8")
    write(export, tmp_path / "out", "toy", icon)
    value = (tmp_path / "out" / "html" / "entities" / "disk-quorum.html").read_text(encoding="utf-8")
    assert 'class="page-case-icon"' in value and 'src="../assets/case-icon.svg"' in value
    index = (tmp_path / "out" / "html" / "index.html").read_text(encoding="utf-8")
    assert 'class="page-case-icon"' not in index
    write(build(_inputs()), tmp_path / "plain", "toy")
    assert 'page-case-icon' not in (tmp_path / "plain" / "html" / "entities" / "disk-quorum.html").read_text(encoding="utf-8")
