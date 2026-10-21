"""Tests for the new GEval criteria added in Plan U6.

Covers the criteria list, their fixed judging steps and their wiring into
``build_metrics()``.
"""

from taxonomy_generator.evaluation.metrics import (
    DOCUMENT_REASON_STEP,
    REASON_STEP,
    TAXONOMY_FORMAT,
    COVERAGE_CRITERION,
    CANDIDATE_COVERAGE_CRITERION,
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
    "One decision point",
    "Rejected-alternative handling",
}


def test_build_metrics_with_coverage_returns_all_ten_criteria():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=True)

    names = {m._criterion.name for m in metrics}  # noqa: SLF001
    assert names == EXPECTED_STRUCTURAL_NAMES | {
        "Dimensional coverage",
        "Candidate-decision coverage",
    }
    assert len(metrics) == 10


def test_build_metrics_without_coverage_omits_document_grounded_criteria():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=False)

    names = {m._criterion.name for m in metrics}  # noqa: SLF001
    assert "Dimensional coverage" not in names
    assert "Candidate-decision coverage" not in names
    assert "One decision point" in names
    assert "Rejected-alternative handling" in names
    assert names == EXPECTED_STRUCTURAL_NAMES
    assert len(metrics) == 8


def test_each_metric_criterion_round_trips_to_correct_criterion_object():
    metrics = build_metrics(model=None, threshold=0.5, include_coverage=True)

    by_name = {m.name: m._criterion for m in metrics}  # noqa: SLF001

    for criterion in STRUCTURAL_CRITERIA:
        assert by_name[criterion.name] is criterion

    assert by_name[COVERAGE_CRITERION.name] is COVERAGE_CRITERION
    assert by_name[CANDIDATE_COVERAGE_CRITERION.name] is CANDIDATE_COVERAGE_CRITERION

    # The GEval instance's own `.criteria` (the judging instructions) must
    # match the criterion's `.criteria` text exactly.
    for metric in metrics:
        assert metric.criteria == metric._criterion.criteria  # noqa: SLF001


def test_every_metric_uses_fixed_steps_with_format_scope_and_actionable_reason():
    for metric in build_metrics(model=None, threshold=0.5, include_coverage=True):
        steps = metric.evaluation_steps
        assert steps, metric.name  # fixed steps: GEval does not regenerate them per call
        assert steps[0] == TAXONOMY_FORMAT
        expected = DOCUMENT_REASON_STEP if metric._criterion.needs_documents else REASON_STEP  # noqa: SLF001
        assert steps[-1] == expected
        assert any(step.startswith("Judge only the criterion") for step in steps)


def test_format_step_accepts_outcomes_and_rules_out_forces():
    assert "'outcome'" in TAXONOMY_FORMAT
    assert "never penalize their absence" in TAXONOMY_FORMAT


def test_one_decision_point_prefers_quality_attribute_grounding_as_secondary():
    criterion = next(c for c in STRUCTURAL_CRITERIA if c.name == "One decision point")
    text = " ".join(criterion.steps)
    assert "one and the same question" in text
    assert "quality-attribute grounding" in text.lower()
    assert "never penalize a well-formed decision point" in text


def test_rejected_alternative_handling_treats_outcome_as_valid():
    criterion = next(c for c in STRUCTURAL_CRITERIA if c.name == "Rejected-alternative handling")
    assert "all four are valid" in " ".join(criterion.steps)


def test_structural_reasons_never_ask_for_additions_and_document_reasons_cite_passages():
    assert "Never ask to add a dimension or value" in REASON_STEP
    assert "passage ids" in DOCUMENT_REASON_STEP


def test_one_decision_point_prefers_merging_single_candidates_over_inventing():
    criterion = next(c for c in STRUCTURAL_CRITERIA if c.name == "One decision point")
    text = " ".join(criterion.steps)
    assert "recommend a split only when every resulting dimension keeps at least two" in text
    assert "Never recommend inventing alternatives" in text


def test_orthogonality_moves_shared_values_instead_of_merging_different_questions():
    criterion = next(c for c in STRUCTURAL_CRITERIA if c.name == "Orthogonality")
    text = " ".join(criterion.steps)
    assert "Recommend merging two dimensions only when they ask the same question" in text
    assert "never recommend merging dimensions that ask different questions" in text
