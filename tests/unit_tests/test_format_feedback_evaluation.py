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
