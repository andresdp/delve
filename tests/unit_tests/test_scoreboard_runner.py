"""Tests for run_scoreboard()'s document-grounded fallback logic (Plan U6).

Plan U6 generalized the no-document placeholder-row logic in
``run_scoreboard()`` from a single hardcoded ``COVERAGE_CRITERION`` row to a
loop over every ``needs_documents=True`` criterion excluded from
``build_metrics()`` (now also ``CANDIDATE_COVERAGE_CRITERION``). These tests
exercise that loop directly, using a fake ``build_metrics`` so no real GEval
judge model / OpenAI API key is required.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest

from taxonomy_generator.evaluation import runner as runner_module
from taxonomy_generator.evaluation.metrics import (
    COVERAGE_CRITERION,
    CANDIDATE_COVERAGE_CRITERION,
    STRUCTURAL_CRITERIA,
    Criterion,
)
from taxonomy_generator.evaluation.runner import (
    format_taxonomy_for_judge,
    run_scoreboard,
    sample_documents,
)


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
        metrics.append(_FakeMetric(CANDIDATE_COVERAGE_CRITERION, 0.6))
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

    assert by_name["Candidate-decision coverage"]["evaluated"] is False
    assert by_name["Candidate-decision coverage"]["score"] is None
    assert by_name["Candidate-decision coverage"]["passed"] is None

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

    assert by_name["Candidate-decision coverage"]["evaluated"] is True
    assert by_name["Candidate-decision coverage"]["score"] == 0.6


def test_judge_view_keeps_structure_and_drops_provenance():
    clusters = [{
        "id": "1", "name": "Drift Detection Test", "description": "Which test detects drift?",
        "relations": [{"target_id": "2", "type": "constrains", "rationale": "long text"}],
        "evidence": {"codes": 3, "documents": 2, "sources": 2},
        "values": [{
            "id": "1.1", "dimension_id": "1", "label": "CUSUM", "description": "d",
            "status": "mixed", "stances": {"accepted": ["s01_p01"]},
            "supporting_doc_ids": ["s01_p01"], "evidence_code_count": 2, "merged_from": [],
        }],
    }]
    view = json.loads(format_taxonomy_for_judge(clusters))
    assert view == [{
        "id": "1", "name": "Drift Detection Test", "description": "Which test detects drift?",
        "relations": [{"target_id": "2", "type": "constrains"}],
        "values": [{"id": "1.1", "label": "CUSUM", "description": "d", "status": "mixed"}],
    }]


def test_sample_is_seeded_and_spread_across_sources():
    docs = [{"id": f"s{s:02d}_p{p:02d}", "content": "x"} for s in range(1, 6) for p in range(1, 11)]
    first = sample_documents(docs, 10, seed=4)
    assert [d["id"] for d in first] == [d["id"] for d in sample_documents(docs, 10, seed=4)]
    sources = {d["id"].split("_")[0] for d in first}
    assert len(sources) == 5  # round-robin over sources, not the first ten passages of s01


def test_small_corpus_is_returned_whole():
    docs = [{"id": "a", "content": "x"}, {"id": "b", "content": "y"}]
    assert sample_documents(docs, 20, seed=None) == docs


def test_coverage_input_prefixes_passage_ids(monkeypatch):
    seen = {}

    def _capture_build_metrics(model, threshold, include_coverage):
        metrics = _fake_build_metrics(model, threshold, include_coverage)
        original = metrics[-1].a_measure

        async def _a_measure(case, _show_indicator=False):
            seen["input"] = case.input
            return await original(case, _show_indicator)

        metrics[-1].a_measure = _a_measure
        return metrics

    monkeypatch.setattr(runner_module, "build_metrics", _capture_build_metrics)
    asyncio.run(run_scoreboard(clusters=[], documents=[{"id": "s03_p02", "content": "text"}],
                               configuration=_config()))
    assert seen["input"] == "[s03_p02] text"
