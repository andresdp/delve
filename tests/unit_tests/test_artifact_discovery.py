"""Tests for sibling-artifact discovery and matching (Plan U4, KTD1)."""

import json
from pathlib import Path

from taxonomy_generator.html_report import discover_siblings, resolve_biplot_path

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "examples" / "cursor-git-at-scale"
FIXTURE_TAXONOMY = FIXTURE_DIR / "cursor-git-at-scale_taxonomy_20260828_212329.json"


def test_real_fixture_resolves_all_four_sibling_kinds():
    """Against the real cursor-git-at-scale fixture, every sibling kind resolves."""
    result = discover_siblings(FIXTURE_TAXONOMY, "cursor-git-at-scale", iteration=4)

    assert result.report is not None
    assert result.report.path.name == "cursor-git-at-scale_report_20260828_212329.md"
    assert result.report.approximate is False

    assert result.documents is not None
    assert result.documents.path.name == "cursor-git-at-scale_documents_20260828_212329.json"
    assert result.documents.approximate is False

    assert result.biplot is not None
    assert result.evaluation is not None


def test_multiple_evaluation_files_exact_match_same_taxonomy_tie_break():
    """Two evaluation JSONs both exact-match source_file; the tie-break picks one via KTD1."""
    result = discover_siblings(FIXTURE_TAXONOMY, "cursor-git-at-scale", iteration=4)

    assert result.evaluation is not None
    # Both taxonomy_evaluation_*.json in the fixture have source_file pointing
    # at this exact taxonomy file, so this exercises the tie-break, not a
    # single unambiguous match.
    assert result.evaluation.approximate is True
    assert result.evaluation.path.name == "taxonomy_evaluation_20260828_213508.json"


def test_biplot_2d_and_3d_both_present_prefers_3d():
    """When both a 2D and 3D biplot match the same stage and iteration, 3D is selected."""
    result = discover_siblings(FIXTURE_TAXONOMY, "cursor-git-at-scale", iteration=4)

    assert result.biplot is not None
    assert result.biplot.path.name == "taxonomy_biplot_cursor-git-at-scale_standalone_4_3d.html"


def test_no_sibling_artifacts_returns_no_match_for_all(tmp_path):
    """A directory with no sibling artifacts: every resolver returns None, nothing raises."""
    taxonomy_path = tmp_path / "solo_taxonomy_20260101_000000.json"
    taxonomy_path.write_text(json.dumps({"taxonomy_name": "solo", "iterations": []}))

    result = discover_siblings(taxonomy_path, "solo", iteration=1)

    assert result.report is None
    assert result.biplot is None
    assert result.evaluation is None
    assert result.documents is None


def test_ambiguous_report_no_exact_timestamp_prefers_timestamped_candidate(tmp_path):
    """No exact-timestamp report match; the candidate with a parseable timestamp wins."""
    taxonomy_path = tmp_path / "ambiguous_taxonomy_20260101_000000.json"
    taxonomy_path.write_text(json.dumps({"taxonomy_name": "ambiguous", "iterations": []}))
    older = tmp_path / "ambiguous_report_20251231_235900.md"
    newer = tmp_path / "ambiguous_report_20260102_010000.md"
    older.write_text("# Grounded Theory Report\n")
    newer.write_text("# Grounded Theory Report\n")

    result = discover_siblings(taxonomy_path, "ambiguous", iteration=1)

    assert result.report is not None
    assert result.report.approximate is True
    assert result.report.path.name == "ambiguous_report_20260102_010000.md"


def test_biplot_iteration_number_is_not_matched_as_a_prefix(tmp_path):
    """Requesting iteration 1 must not match a biplot file for iteration 10 (or 11, 19, ...)."""
    decoy = tmp_path / "taxonomy_biplot_solo_standalone_10_2d.html"
    decoy.write_text("<html></html>")

    result = resolve_biplot_path(tmp_path, "solo", iteration=1)

    assert result is None

    real = tmp_path / "taxonomy_biplot_solo_standalone_1_2d.html"
    real.write_text("<html></html>")

    result = resolve_biplot_path(tmp_path, "solo", iteration=1)

    assert result is not None
    assert result.path.name == "taxonomy_biplot_solo_standalone_1_2d.html"
