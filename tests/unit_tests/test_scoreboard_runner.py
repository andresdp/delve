"""Tests for run_scoreboard()'s document-grounded fallback logic (Plan U6).

Plan U6 generalized the no-document placeholder-row logic in
``run_scoreboard()`` from a single hardcoded ``COVERAGE_CRITERION`` row to a
loop over every ``needs_documents=True`` criterion excluded from
``build_metrics()`` (now also ``GAP_AWARENESS_CRITERION``). These tests
exercise that loop directly, using a fake ``build_metrics`` so no real GEval
judge model / OpenAI API key is required.
"""

import asyncio
from types import SimpleNamespace

import pytest

from taxonomy_generator.evaluation import runner as runner_module
from taxonomy_generator.evaluation.metrics import (
    COVERAGE_CRITERION,
    GAP_AWARENESS_CRITERION,
    STRUCTURAL_CRITERIA,
    Criterion,
)
from taxonomy_generator.evaluation.runner import run_scoreboard


class _FakeMetric:
    """Stand-in for a GEval instance: records the criterion and a canned score."""

    def __init__(self, criterion: Criterion, score: float):
        self._criterion = criterion
        self.score = score
        self.reason = "fake reason"

    async def a_measure(self, case, _show_indicator=False):
        return None


def _fake_build_metrics(model, threshold, include_coverage):
    metrics = [_FakeMetric(c, 0.9) for c in STRUCTURAL_CRITERIA]
    if include_coverage:
        metrics.append(_FakeMetric(COVERAGE_CRITERION, 0.7))
        metrics.append(_FakeMetric(GAP_AWARENESS_CRITERION, 0.6))
    return metrics


def _config():
    return SimpleNamespace(
        evaluation_judge_model=None,
        model=None,
        evaluation_threshold=0.5,
        use_case="Route support tickets",
        evaluation_max_documents=10,
    )


def test_no_documents_lists_both_document_grounded_criteria_as_not_evaluated(monkeypatch):
    monkeypatch.setattr(runner_module, "build_metrics", _fake_build_metrics)

    result = asyncio.run(run_scoreboard(clusters=[], documents=None, configuration=_config()))

    assert result["unavailable"] is False
    by_name = {row["name"]: row for row in result["criteria"]}

    assert by_name["Dimensional coverage"]["evaluated"] is False
    assert by_name["Dimensional coverage"]["score"] is None
    assert by_name["Dimensional coverage"]["passed"] is None

    assert by_name["Design-space gap awareness"]["evaluated"] is False
    assert by_name["Design-space gap awareness"]["score"] is None
    assert by_name["Design-space gap awareness"]["passed"] is None

    # Structural criteria were still measured and scored normally.
    assert by_name["Orthogonality"]["evaluated"] is True
    assert by_name["Orthogonality"]["score"] == 0.9

    # Overall score excludes the unevaluated placeholder rows.
    assert result["overall"] == pytest.approx(0.9)


def test_with_documents_scores_both_document_grounded_criteria(monkeypatch):
    monkeypatch.setattr(runner_module, "build_metrics", _fake_build_metrics)

    docs = [{"content": "a document"}]
    result = asyncio.run(run_scoreboard(clusters=[], documents=docs, configuration=_config()))

    by_name = {row["name"]: row for row in result["criteria"]}

    assert by_name["Dimensional coverage"]["evaluated"] is True
    assert by_name["Dimensional coverage"]["score"] == 0.7

    assert by_name["Design-space gap awareness"]["evaluated"] is True
    assert by_name["Design-space gap awareness"]["score"] == 0.6
