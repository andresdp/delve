"""Tests for the test-mode evaluation detour in should_aggregate_values (Plan U3)."""

from taxonomy_generator.routing.should_aggregate_values import should_aggregate_values
from taxonomy_generator.state import State


def _config(mode: str, evaluation_enabled: bool) -> dict:
    return {"configurable": {"mode": mode, "evaluation_enabled": evaluation_enabled}}


def test_train_mode_ends_run_unchanged():
    result = should_aggregate_values(State(), _config("train", evaluation_enabled=True))
    assert result == "__end__"


def test_test_mode_with_evaluation_enabled_routes_through_final_evaluator():
    result = should_aggregate_values(State(), _config("test", evaluation_enabled=True))
    assert result == "evaluate_taxonomy"


def test_test_mode_with_evaluation_disabled_routes_directly_to_aggregation():
    result = should_aggregate_values(State(), _config("test", evaluation_enabled=False))
    assert result == "aggregate_new_values"
