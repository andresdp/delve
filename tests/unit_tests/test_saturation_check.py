"""Saturation is tested on new data: the latest minibatch vs the taxonomy before it."""

import asyncio

from langchain_core.runnables import RunnableLambda

from taxonomy_generator.nodes import saturation_checker as checker_module
from taxonomy_generator.nodes.saturation_checker import check_saturation
from taxonomy_generator.schemas import SaturationCheckOutput
from taxonomy_generator.state import State

DOCS = [{"id": "d1", "content": "a"}, {"id": "d2", "content": "b"}]
CODES = [{"doc_id": "d2", "label": "CUSUM test", "rationale": "r", "status": "accepted"}]
BEFORE = [{"id": "1", "name": "Before batch", "description": ""}]
AFTER = [{"id": "1", "name": "After batch", "description": ""}]


def _config():
    return {"configurable": {"saturation_min_coverage": 0.9}}


def _fake_chain(seen, saturated):
    def _invoke(inputs):
        seen.append(inputs)
        return SaturationCheckOutput(
            is_saturated=saturated,
            uncovered_concepts=[] if saturated else ["CUSUM test"],
            rationale="r",
        )
    return lambda configuration: RunnableLambda(_invoke)


def test_generation_batch_is_not_tested_or_counted(monkeypatch):
    seen = []
    monkeypatch.setattr(checker_module, "_setup_saturation_chain", _fake_chain(seen, True))
    state = State(documents=DOCS, minibatches=[[0], [1]], open_code_batch_index=1,
                  clusters=[AFTER], open_codes=CODES, saturation_streak=0)

    result = asyncio.run(check_saturation(state, _config()))

    assert seen == []  # no LLM call
    assert result["saturation_streak"] == 0
    assert result["saturation_history"][0]["is_saturated"] is False
    assert result["saturation_history"][0]["coverage"] is None


def test_new_batch_is_tested_against_the_taxonomy_before_it(monkeypatch):
    seen = []
    monkeypatch.setattr(checker_module, "_setup_saturation_chain", _fake_chain(seen, True))
    state = State(documents=DOCS, minibatches=[[0], [1]], open_code_batch_index=2,
                  clusters=[BEFORE, AFTER], open_codes=CODES, saturation_streak=1)

    result = asyncio.run(check_saturation(state, _config()))

    assert "Before batch" in seen[0]["taxonomy_json"]
    assert "After batch" not in seen[0]["taxonomy_json"]
    assert "CUSUM test" in seen[0]["codes_json"]
    assert result["saturation_streak"] == 2


def test_uncovered_concepts_reset_the_streak_and_become_critic_feedback(monkeypatch):
    monkeypatch.setattr(checker_module, "_setup_saturation_chain", _fake_chain([], False))
    state = State(documents=DOCS, minibatches=[[0], [1]], open_code_batch_index=2,
                  clusters=[BEFORE, AFTER], open_codes=CODES, saturation_streak=2)

    result = asyncio.run(check_saturation(state, _config()))

    assert result["saturation_streak"] == 0
    assert "CUSUM test" in result["user_feedback"].feedback
