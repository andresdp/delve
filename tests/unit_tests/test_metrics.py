"""Tests for the new GEval criteria added in Plan U6.

Covers the three new ``Criterion`` entries (Quality-Attribute Grounding,
Rejected-Alternative Handling, Design-Space Gap Awareness) and their wiring
into ``build_metrics()``.
"""

from taxonomy_generator.evaluation.metrics import (
    COVERAGE_CRITERION,
    GAP_AWARENESS_CRITERION,
    STRUCTURAL_CRITERIA,
    build_metrics,
)

EXPECTED_STRUCTURAL_NAMES = {
    "Orthogonality",
    "Clarity",
    "Completeness",
    "Use case alignment",
    "No catch-alls",
    "Axis vs. value",
    "Quality-attribute grounding",
    "Rejected-alternative handling",
}


def test_build_metrics_with_coverage_returns_all_ten_criteria():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=True)

    names = {m._criterion.name for m in metrics}  # noqa: SLF001
    assert names == EXPECTED_STRUCTURAL_NAMES | {
        "Dimensional coverage",
        "Design-space gap awareness",
    }
    assert len(metrics) == 10


def test_build_metrics_without_coverage_omits_document_grounded_criteria():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=False)

    names = {m._criterion.name for m in metrics}  # noqa: SLF001
    assert "Dimensional coverage" not in names
    assert "Design-space gap awareness" not in names
    assert "Quality-attribute grounding" in names
    assert "Rejected-alternative handling" in names
    assert names == EXPECTED_STRUCTURAL_NAMES
    assert len(metrics) == 8


def test_each_metric_criterion_round_trips_to_correct_criterion_object():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=True)

    by_name = {m.name: m._criterion for m in metrics}  # noqa: SLF001

    for criterion in STRUCTURAL_CRITERIA:
        assert by_name[criterion.name] is criterion

    assert by_name[COVERAGE_CRITERION.name] is COVERAGE_CRITERION
    assert by_name[GAP_AWARENESS_CRITERION.name] is GAP_AWARENESS_CRITERION

    # The GEval instance's own `.criteria` (the judging instructions) must
    # match the criterion's `.criteria` text exactly.
    for metric in metrics:
        assert metric.criteria == metric._criterion.criteria  # noqa: SLF001
