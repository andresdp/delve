"""Tests for the HTML section-rendering module (Plan U3)."""

import json
from pathlib import Path

from taxonomy_generator import html_report as hr

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "examples" / "cursor-git-at-scale"
FIXTURE_TAXONOMY = FIXTURE_DIR / "cursor-git-at-scale_taxonomy_20260828_212329.json"

_MERMAID_JS_STUB = "/* mermaid stub */"
_PLOTLYJS_STUB = "/* plotly stub */"


def _load_real_fixture():
    taxonomy_data = json.loads(FIXTURE_TAXONOMY.read_text())
    siblings = hr.discover_siblings(FIXTURE_TAXONOMY, "cursor-git-at-scale", iteration=4)
    report_text = siblings.report.path.read_text() if siblings.report else None
    biplot_text = siblings.biplot.path.read_text() if siblings.biplot else None
    documents_data = json.loads(siblings.documents.path.read_text()) if siblings.documents else None
    evaluation_data = json.loads(siblings.evaluation.path.read_text()) if siblings.evaluation else None
    view_clusters = taxonomy_data["iterations"][-1]["clusters"]
    return taxonomy_data, view_clusters, report_text, biplot_text, documents_data, evaluation_data


def test_full_data_present_renders_every_section_no_external_refs():
    """With all four siblings present, every section renders in order with no external refs."""
    taxonomy_data, view_clusters, report_text, biplot_text, documents_data, evaluation_data = _load_real_fixture()

    page = hr.render_html_report(
        "cursor-git-at-scale",
        taxonomy_data,
        view_clusters,
        dropped_dimensions=[],
        all_clusters_for_dropped=view_clusters,
        documents_data=documents_data,
        report_md_text=report_text,
        biplot_html_text=biplot_text,
        evaluation_data=evaluation_data,
        mermaid_js=_MERMAID_JS_STUB,
        plotlyjs_js=_PLOTLYJS_STUB,
    )

    for heading in ["Run Summary", "Dimension Diagram", "Dimension Catalog", "Narrative Summary", "Biplot", "Evaluation"]:
        assert f"<h2>{heading}</h2>" in page

    assert "flowchart TB" in page  # the diagram's mermaid syntax
    assert _MERMAID_JS_STUB in page  # vendored Mermaid JS inlined, not just absent CDN ref
    assert 'class="plotly-graph-div"' in page  # extracted Plotly chart div
    assert "<script src=" not in page
    assert "<link href=" not in page

    # Diagram appears before Catalog appears before Narrative, per KTD5's fixed order.
    assert page.index("Dimension Diagram") < page.index("Dimension Catalog") < page.index("Narrative Summary")


def test_missing_biplot_sibling_renders_not_available():
    """A missing biplot sibling renders an explicit "not available" note, not an exception."""
    section = hr.render_biplot_section(None)
    assert "No biplot is available" in section
    assert "plotly-graph-div" not in section


def test_malformed_biplot_sibling_falls_back_to_not_available():
    """A biplot file present but lacking the expected div/script shape falls back like a missing one."""
    section = hr.render_biplot_section("<html><body>not a plotly export</body></html>")
    assert "No biplot is available" in section
    assert "plotly-graph-div" not in section


def test_missing_vs_unavailable_evaluation_render_distinct_text():
    """A missing evaluation sibling and one present with unavailable: true render different text."""
    missing = hr.render_evaluation_section(None)
    unavailable = hr.render_evaluation_section(
        {"scoreboard": {"unavailable": True, "error": "judge model unreachable"}}
    )
    assert missing != unavailable
    assert "No evaluation was run" in missing
    assert "judge model unreachable" in unavailable


def test_zero_discarded_and_zero_labeled_documents_render_none_found():
    """Legitimately empty results render a distinct "none found" state, not "not available"."""
    discarded_section = hr.render_discarded_section([], [])
    assert discarded_section == ""  # per KTD5, omitted entirely when empty

    labeling_html = hr.render_document_labeling({"taxonomy_name": "x", "documents": []})
    assert "No labeled documents found" in labeling_html
    assert "not available" not in labeling_html

    missing_labeling_html = hr.render_document_labeling(None)
    assert "not available" in missing_labeling_html


def test_missing_documents_sibling_run_summary_shows_not_available():
    """A missing documents-JSON sibling: the labeling table is unavailable, the rest still renders."""
    taxonomy_data = {
        "taxonomy_name": "solo",
        "mode": "train",
        "iterations": [{"explanation": "seed", "clusters": [{"id": "1", "name": "Dim", "values": []}]}],
    }
    section = hr.render_run_summary(taxonomy_data, documents_data=None)
    assert "not available" in section
    assert "Dim" in section  # dimension table still rendered


def test_narrative_extraction_stops_at_next_heading():
    """Narrative extraction stops at the next '## ' heading, not bleeding into the diagram section."""
    report_md = (
        "# Grounded Theory Report\n\n"
        "## Narrative Summary\n\n"
        "This is the real narrative text.\n\n"
        "## Dimension Relationship Diagram\n\n"
        "```mermaid\nflowchart TB\n```\n"
    )
    section = hr.render_narrative_section(report_md)
    assert "This is the real narrative text." in section
    assert "flowchart TB" not in section


def test_narrative_normalizes_bold_and_list_markdown():
    """Embedded **bold** and a leading '- ' list line normalize to HTML, not literal markdown."""
    report_md = (
        "## Narrative Summary\n\n"
        "This taxonomy has **three** key dimensions.\n\n"
        "- First point\n"
        "- Second point\n"
    )
    section = hr.render_narrative_section(report_md)
    assert "<strong>three</strong>" in section
    assert "**three**" not in section
    assert "<li>First point</li>" in section
    assert "<li>Second point</li>" in section


def test_catalog_shows_merged_from_consolidation_note():
    """A value carrying merged_from provenance shows the consolidation note (report_renderer parity)."""
    clusters = [
        {
            "id": "1",
            "name": "Dim One",
            "description": "desc",
            "values": [
                {
                    "label": "Canonical Value",
                    "description": "desc",
                    "merged_from": [{"label": "Draft A"}, {"label": "Draft B"}],
                }
            ],
            "relations": [],
        }
    ]
    section = hr.render_catalog_section(clusters)
    assert "consolidated with 2 similar values" in section
    assert "Draft A" in section and "Draft B" in section
