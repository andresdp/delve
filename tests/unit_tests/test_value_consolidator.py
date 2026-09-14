"""Tests for status-aware value merging in consolidate_values (Plan U4)."""

import asyncio
import math
from unittest.mock import AsyncMock

import numpy as np

from taxonomy_generator.nodes import value_consolidator as consolidator_module
from taxonomy_generator.nodes.value_consolidator import consolidate_values
from taxonomy_generator.schemas import ValueMergeOutput
from taxonomy_generator.state import State


def _config(**overrides) -> dict:
    configurable = {
        "mode": "train",
        "visualization_enabled": False,
        "value_merge_distance_threshold": 0.2,
        "value_merge_borderline_band": 0.08,
        **overrides,
    }
    return {"configurable": configurable}


def _unit(angle_degrees: float) -> list:
    """A 2D unit vector at the given angle — already L2-normalized."""
    rad = math.radians(angle_degrees)
    return [math.cos(rad), math.sin(rad)]


class _FakeEmbeddings:
    """Returns pre-baked vectors in call order, ignoring the input text."""

    def __init__(self, vectors: list):
        self._vectors = vectors

    async def aembed_documents(self, texts):
        assert len(texts) == len(self._vectors), (
            f"expected {len(self._vectors)} texts, got {len(texts)}"
        )
        return self._vectors


def _patch_embeddings(monkeypatch, vectors: list):
    monkeypatch.setattr(
        consolidator_module, "load_embeddings_model", lambda name: _FakeEmbeddings(vectors)
    )


def _patch_merge_chain(monkeypatch, same_decision: bool = True):
    """Patch _setup_merge_chain to return a chain whose ainvoke is an AsyncMock."""
    fake_chain = AsyncMock()
    fake_chain.ainvoke = AsyncMock(
        return_value=ValueMergeOutput(same_decision=same_decision, rationale="test rationale")
    )
    monkeypatch.setattr(consolidator_module, "_setup_merge_chain", lambda configuration: fake_chain)
    return fake_chain


def _value(vid, label, status=None, description="desc"):
    v = {
        "id": vid,
        "dimension_id": "1",
        "label": label,
        "description": description,
        "supporting_doc_ids": [],
    }
    if status is not None:
        v["status"] = status
    return v


def test_same_status_pair_below_epsilon_merges_and_preserves_status(monkeypatch):
    """Two same-status values within epsilon merge; status is preserved."""
    values = [
        _value("1.1", "Accept refund", status="accepted"),
        _value("1.2", "Approve refund", status="accepted"),
    ]
    vectors = [_unit(0), _unit(5)]  # distance ~0.087, well below epsilon=0.2

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    _patch_merge_chain(monkeypatch)
    result = asyncio.run(consolidate_values(state, _config()))

    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 1
    assert new_values[0]["status"] == "accepted"
    assert new_values[0]["id"] == "1.1"
    assert len(new_values[0]["merged_from"]) == 1


def test_different_status_pair_below_epsilon_does_not_merge(monkeypatch):
    """Two values close enough to merge under the old algorithm, but of
    different status, must stay separate under status-partitioned merging."""
    values = [
        _value("1.1", "Accept refund", status="accepted"),
        _value("1.2", "Reject refund", status="rejected"),
    ]
    vectors = [_unit(0), _unit(5)]  # distance ~0.087, well below epsilon=0.2

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    _patch_merge_chain(monkeypatch)
    result = asyncio.run(consolidate_values(state, _config()))

    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 2
    by_id = {v["id"]: v for v in new_values}
    assert {v["status"] for v in new_values} == {"accepted", "rejected"}
    assert {v["label"] for v in new_values} == {"Accept refund", "Reject refund"}
    # Renumbered once across the whole dimension, in some deterministic order.
    assert set(by_id.keys()) == {"1.1", "1.2"}


def test_three_statuses_far_apart_retain_status_and_renumber(monkeypatch):
    """Three values spanning all three statuses, all far apart, produce
    three distinct values retaining their original status, renumbered
    dim_id.1 - dim_id.3."""
    values = [
        _value("1.1", "Accepted decision", status="accepted"),
        _value("1.2", "Rejected decision", status="rejected"),
        _value("1.3", "Outcome decision", status="outcome"),
    ]
    # Far apart: 0, 90, 180 degrees -> all pairwise distances > borderline_upper (0.28)
    vectors = [_unit(0), _unit(90), _unit(180)]

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    fake_chain = _patch_merge_chain(monkeypatch)
    result = asyncio.run(consolidate_values(state, _config()))

    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 3
    ids = sorted(v["id"] for v in new_values)
    assert ids == ["1.1", "1.2", "1.3"]
    statuses_by_label = {v["label"]: v["status"] for v in new_values}
    assert statuses_by_label == {
        "Accepted decision": "accepted",
        "Rejected decision": "rejected",
        "Outcome decision": "outcome",
    }
    # No borderline pairs (all far apart) -> no LLM calls.
    fake_chain.ainvoke.assert_not_called()


def test_borderline_cross_status_pair_skips_llm_adjudication(monkeypatch):
    """A borderline-distance pair of different status must never reach the
    LLM adjudication call — partitioning happens before borderline pairing."""
    values = [
        _value("1.1", "Accept refund", status="accepted"),
        _value("1.2", "Reject refund", status="rejected"),
    ]
    # angle=14deg -> distance = 2*sin(7deg) ~= 0.2437, between epsilon (0.2)
    # and borderline_upper (0.28): a borderline pair under the old
    # same-dimension algorithm.
    vectors = [_unit(0), _unit(14)]
    d = float(np.linalg.norm(np.array(vectors[0]) - np.array(vectors[1])))
    assert 0.2 < d <= 0.28, f"test vectors not in the borderline band: d={d}"

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    fake_chain = _patch_merge_chain(monkeypatch)
    result = asyncio.run(consolidate_values(state, _config()))

    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 2  # not merged
    fake_chain.ainvoke.assert_not_called()


def test_borderline_same_status_pair_invokes_llm_and_can_merge(monkeypatch):
    """Sanity check for the borderline test geometry: a same-status
    borderline pair DOES reach the LLM and, on approval, merges."""
    values = [
        _value("1.1", "Accept refund", status="accepted"),
        _value("1.2", "Approve refund", status="accepted"),
    ]
    vectors = [_unit(0), _unit(14)]  # same borderline distance as above

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    fake_chain = _patch_merge_chain(monkeypatch, same_decision=True)
    result = asyncio.run(consolidate_values(state, _config()))

    fake_chain.ainvoke.assert_called_once()
    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 1
    assert new_values[0]["status"] == "accepted"


def test_legacy_value_missing_status_key_treated_as_accepted(monkeypatch):
    """A value dict with no 'status' key (legacy shape, pre-dating this
    change) is treated as 'accepted' via .get, and merges with an explicit
    'accepted' value when close enough."""
    values = [
        _value("1.1", "Accept refund", status=None),  # no "status" key at all
        _value("1.2", "Approve refund", status="accepted"),
    ]
    assert "status" not in values[0]

    vectors = [_unit(0), _unit(5)]  # well below epsilon

    state = State(clusters=[[{"id": "1", "name": "Refunds", "description": "d", "values": values}]])

    _patch_embeddings(monkeypatch, vectors)
    _patch_merge_chain(monkeypatch)
    result = asyncio.run(consolidate_values(state, _config()))

    new_values = result["clusters"][0][0]["values"]
    assert len(new_values) == 1
    assert new_values[0]["status"] == "accepted"
