"""Tests for format_feedback's evaluation-summary section (Plan U4)."""

from taxonomy_generator.state import State, UserFeedback
from taxonomy_generator.utils import format_feedback

SCOREBOARD = {
    "criteria": [
        {"name": "Orthogonality", "score": 0.9, "threshold": 0.5, "evaluated": True, "passed": True, "reason": ""},
        {"name": "Dimensional coverage", "score": 0.6, "threshold": 0.5, "evaluated": True, "passed": True, "reason": ""},
        {"name": "Clarity", "score": 0.75, "threshold": 0.5, "evaluated": True, "passed": True, "reason": ""},
        {"name": "Use case alignment", "score": None, "threshold": 0.5, "evaluated": False, "passed": None, "reason": ""},
    ],
    "overall": 0.75,
    "model": "gpt-test",
    "unavailable": False,
}


def test_no_evaluation_history_omits_section_and_returns_none_sentinel():
    state = State()
    assert format_feedback(state) == "None."


def test_unavailable_latest_entry_omits_section():
    state = State(evaluation_history=[{"criteria": [], "overall": None, "model": "x", "unavailable": True}])
    assert format_feedback(state) == "None."


def test_scoreboard_renders_weakest_criterion_first_and_excludes_unevaluated():
    state = State(evaluation_history=[SCOREBOARD])
    result = format_feedback(state)

    assert "overall 0.75" in result
    assert "Use case alignment" not in result  # evaluated: False, excluded

    coverage_idx = result.index("Dimensional coverage")
    clarity_idx = result.index("Clarity")
    orthogonality_idx = result.index("Orthogonality")
    assert coverage_idx < clarity_idx < orthogonality_idx  # weakest (0.6) first


def test_evaluation_section_coexists_with_external_and_user_feedback():
    external = UserFeedback(decision="modify", explanation="scope narrowed", feedback="focus on billing")
    user_feedback = UserFeedback(decision="modify", explanation="gap found", feedback="add onboarding dimension")
    state = State(
        external_feedback=external,
        user_feedback=user_feedback,
        evaluation_history=[SCOREBOARD],
    )
    result = format_feedback(state)

    assert "focus on billing" in result
    assert "add onboarding dimension" in result
    assert "Automated evaluation summary" in result
    # Evaluation section comes last.
    assert result.index("Automated evaluation summary") > result.index("add onboarding dimension")


FAILING = {
    "criteria": [
        {"name": "Orthogonality", "score": 0.3, "threshold": 0.5, "evaluated": True, "passed": False,
         "reason": "Dimensions 2 and 5 ask the same question; merge dimension 5 into 2."},
        {"name": "One decision point", "score": 0.2, "threshold": 0.5, "evaluated": True, "passed": False,
         "reason": "Dimension 3 'Governance' bundles two questions; split it."},
        {"name": "No catch-alls", "score": 0.9, "threshold": 0.5, "evaluated": True, "passed": True,
         "reason": "None found."},
    ],
    "overall": 0.47,
    "model": "gpt-test",
    "unavailable": False,
}


def test_failing_criteria_pass_the_judges_reasons_weakest_first():
    result = format_feedback(State(evaluation_history=[FAILING]))

    assert "split it" in result and "merge dimension 5 into 2" in result
    assert result.index("One decision point") < result.index("Orthogonality")
    # Passing criteria are listed to preserve, without their reasons.
    assert "Passing criteria (preserve what they reward): No catch-alls 0.90" in result
    assert "None found." not in result
    # The instruction says these issues apply even when the new data does not show them.
    assert "even if the new documents do not show them" in result


def test_long_reasons_are_shortened():
    long_board = {**FAILING, "criteria": [{**FAILING["criteria"][0], "reason": "word " * 500}]}
    result = format_feedback(State(evaluation_history=[long_board]))
    assert "…" in result
    assert len(result) < 2000


def test_failing_criteria_beyond_the_limit_are_not_called_passing():
    criteria = [
        {"name": f"C{i}", "score": 0.1 * i, "threshold": 0.5, "evaluated": True, "reason": f"fix {i}"}
        for i in range(1, 8)
    ]
    result = format_feedback(State(evaluation_history=[{**FAILING, "criteria": criteria}]))
    assert "Also below the threshold (address after the issues above): C6 0.60" not in result
    assert "C5 0.50" in result  # 0.5 is not below the threshold: passing
    issues, _, tail = result.partition("Passing criteria")
    assert "fix 4" in issues and "fix 5" not in issues
    assert "C5 0.50" in tail and "C1" not in tail


def test_more_than_five_failing_criteria_list_the_rest_as_below_threshold():
    criteria = [
        {"name": f"C{i}", "score": 0.1 * i, "threshold": 0.9, "evaluated": True, "reason": f"fix {i}"}
        for i in range(1, 8)
    ]
    result = format_feedback(State(evaluation_history=[{**FAILING, "criteria": criteria}]))
    assert "Also below the threshold (address after the issues above): C6 0.60, C7 0.70." in result
    assert "Passing criteria" not in result


def test_excluded_criteria_are_not_fed_back():
    board = {**FAILING, "criteria": FAILING["criteria"] + [
        {"name": "Completeness", "score": 0.1, "threshold": 0.5, "evaluated": True, "passed": False,
         "reason": "Add an API gateway dimension."},
    ]}
    result = format_feedback(State(evaluation_history=[board]), exclude_criteria=("Completeness",))
    assert "Completeness" not in result and "API gateway" not in result
    assert "merge dimension 5 into 2" in result
    assert "Never add a dimension or value that no open code supports" in result


def test_completeness_is_excluded_by_default_in_the_configuration():
    from taxonomy_generator.configuration import Configuration

    configuration = Configuration.from_runnable_config(None)
    assert "Completeness" in configuration.evaluation_feedback_exclude
