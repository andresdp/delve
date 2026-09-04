"""End-to-end test for the --html-report CLI mode (Plan U5, main.py:_run_html_report)."""

import argparse
import asyncio
import json
from pathlib import Path

import main as main_module

NAME = "solo"
TIMESTAMP = "20260101_000000"


def _write_full_sibling_set(directory: Path) -> Path:
    """Write a taxonomy JSON plus all four sibling artifacts into directory."""
    taxonomy_path = directory / f"{NAME}_taxonomy_{TIMESTAMP}.json"
    clusters = [
        {
            "id": "1",
            "name": "Dim",
            "description": "d",
            "values": [{"label": "V", "description": "vd"}],
            "relations": [],
        }
    ]
    taxonomy_data = {
        "taxonomy_name": NAME,
        "mode": "train",
        "run_metrics": {
            "elapsed_seconds": 1.0,
            "total_tokens": 10,
            "prompt_tokens": 5,
            "completion_tokens": 5,
        },
        "iterations": [{"explanation": "seed", "clusters": clusters}],
        "selected_clusters": clusters,
    }
    taxonomy_path.write_text(json.dumps(taxonomy_data))

    (directory / f"{NAME}_report_{TIMESTAMP}.md").write_text(
        "# Grounded Theory Report\n\n"
        "## Narrative Summary\n\n"
        "This is the narrative.\n\n"
        "## Dimension Relationship Diagram\n\n"
        "```mermaid\nflowchart TB\n```\n"
    )
    (directory / f"taxonomy_biplot_{NAME}_standalone_1_2d.html").write_text(
        '<div id="x" class="plotly-graph-div" style="height:100%"></div>'
        '<script>Plotly.newPlot("x", [], {})</script>'
    )
    (directory / f"taxonomy_evaluation_{TIMESTAMP}.json").write_text(
        json.dumps(
            {
                "taxonomy_name": NAME,
                "source_file": str(taxonomy_path),
                "iteration": 1,
                "scoreboard": {"criteria": [], "overall": None, "model": "m", "unavailable": False},
            }
        )
    )
    (directory / f"{NAME}_documents_{TIMESTAMP}.json").write_text(
        json.dumps({"taxonomy_name": NAME, "documents": [{"category": "Dim", "score": 0.9, "content": "doc"}]})
    )
    return taxonomy_path


def test_run_html_report_end_to_end_writes_self_contained_page(tmp_path):
    """--html-report writes one self-contained HTML file combining all sibling artifacts."""
    taxonomy_path = _write_full_sibling_set(tmp_path)
    out_dir = tmp_path / "out"
    args = argparse.Namespace(
        html_report=str(taxonomy_path), output=str(out_dir), iteration=None, config=None,
    )

    asyncio.run(main_module._run_html_report(args))

    out_files = list(out_dir.glob("*_html_report_*.html"))
    assert len(out_files) == 1
    content = out_files[0].read_text()
    assert "<script src=" not in content
    assert "<link href=" not in content
    assert "This is the narrative." in content
    assert "plotly-graph-div" in content


def test_run_html_report_without_output_writes_next_to_taxonomy_file(tmp_path):
    """No --output: the report lands in the taxonomy file's own folder (matches --visualize)."""
    taxonomy_path = _write_full_sibling_set(tmp_path)
    args = argparse.Namespace(
        html_report=str(taxonomy_path), output=None, iteration=None, config=None,
    )

    asyncio.run(main_module._run_html_report(args))

    out_files = list(tmp_path.glob("*_html_report_*.html"))
    assert len(out_files) == 1


def test_run_html_report_with_no_siblings_still_writes_a_page(tmp_path):
    """A taxonomy JSON with no sibling artifacts at all still produces a page, not a crash."""
    taxonomy_path = tmp_path / f"lonely_taxonomy_{TIMESTAMP}.json"
    clusters = [{"id": "1", "name": "Dim", "description": "d", "values": [], "relations": []}]
    taxonomy_path.write_text(
        json.dumps({"taxonomy_name": "lonely", "iterations": [{"explanation": "seed", "clusters": clusters}]})
    )
    out_dir = tmp_path / "out"
    args = argparse.Namespace(
        html_report=str(taxonomy_path), output=str(out_dir), iteration=None, config=None,
    )

    asyncio.run(main_module._run_html_report(args))

    out_files = list(out_dir.glob("*_html_report_*.html"))
    assert len(out_files) == 1
    content = out_files[0].read_text()
    assert "not available" in content.lower() or "no biplot is available" in content.lower()
