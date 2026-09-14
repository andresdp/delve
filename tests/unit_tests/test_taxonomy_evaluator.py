"""Tests for the observe-only evaluate_taxonomy node (Plan U1)."""

import asyncio

from taxonomy_generator.nodes import taxonomy_evaluator as evaluator_module
from taxonomy_generator.nodes.taxonomy_evaluator import evaluate_taxonomy
from taxonomy_generator.state import State


def _config(**overrides) -> dict:
    return {"configurable": {"mode": "train", "evaluation_enabled": True, **overrides}}


def test_disabled_evaluation_returns_empty_history_without_scoring(monkeypatch):
    async def _boom(*args, **kwargs):
        raise AssertionError("run_scoreboard must not be called when evaluation is disabled")

    monkeypatch.setattr(evaluator_module, "run_scoreboard", _boom)

    state = State(clusters=[[{"id": "c1", "name": "Billing", "description": "desc"}]])
    result = asyncio.run(evaluate_taxonomy(state, _config(evaluation_enabled=False)))

    assert result["evaluation"] is None
    assert result["evaluation_history"] == []
    assert "clusters" not in result
    assert "selected_clusters" not in result
    assert "documents" not in result


def test_no_taxonomy_view_returns_empty_history_without_scoring(monkeypatch):
    async def _boom(*args, **kwargs):
        raise AssertionError("run_scoreboard must not be called with no taxonomy view")

    monkeypatch.setattr(evaluator_module, "run_scoreboard", _boom)

    state = State(clusters=[])
    result = asyncio.run(evaluate_taxonomy(state, _config()))

    assert result["evaluation"] is None
    assert result["evaluation_history"] == []


def test_successful_scoring_returns_single_item_history(monkeypatch):
    scoreboard = {
        "criteria": [{"name": "Clarity", "score": 0.8, "threshold": 0.5, "evaluated": True, "passed": True, "reason": ""}],
        "overall": 0.8,
        "model": "gpt-test",
        "unavailable": False,
    }

    async def _fake_run_scoreboard(view, documents, configuration):
        return scoreboard

    monkeypatch.setattr(evaluator_module, "run_scoreboard", _fake_run_scoreboard)

    state = State(clusters=[[{"id": "c1", "name": "Billing", "description": "desc"}]])
    result = asyncio.run(evaluate_taxonomy(state, _config()))

    assert result["evaluation"] == scoreboard
    # The node returns only this call's entry — the state reducer owns
    # accumulation, not the node itself.
    assert result["evaluation_history"] == [scoreboard]
    assert "clusters" not in result
    assert "selected_clusters" not in result
    assert "documents" not in result


def test_judge_failure_degrades_to_unavailable_scoreboard(monkeypatch):
    async def _unavailable(view, documents, configuration):
        return {"criteria": [], "overall": None, "model": "gpt-test", "unavailable": True, "error": "boom"}

    monkeypatch.setattr(evaluator_module, "run_scoreboard", _unavailable)

    state = State(clusters=[[{"id": "c1", "name": "Billing", "description": "desc"}]])
    result = asyncio.run(evaluate_taxonomy(state, _config()))

    assert result["evaluation"]["unavailable"] is True
    assert result["evaluation_history"] == [result["evaluation"]]
