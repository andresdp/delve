"""Tests for status defaulting in aggregate_new_values (Plan U4)."""

import asyncio

from taxonomy_generator.nodes import value_aggregator as aggregator_module
from taxonomy_generator.nodes.value_aggregator import aggregate_new_values
from taxonomy_generator.state import Doc, State


def _config(**overrides) -> dict:
    configurable = {
        "mode": "test",
        "fallback_category": "Other",
        "value_merge_distance_threshold": 0.2,
        **overrides,
    }
    return {"configurable": configurable}


def test_new_value_appended_in_test_mode_sets_status_accepted(monkeypatch):
    """A newly aggregated value (Test Mode's new-value append path) must
    carry status='accepted' — R5."""
    # No existing values for the dimension, so the proposal survives dedup
    # without needing the embedding path at all.
    clusters = [{"id": "1", "name": "Refunds", "description": "d", "values": []}]
    documents = [
        Doc(id="doc-1", content="c", category="Refunds", value="Store credit only"),
    ]
    state = State(clusters=[clusters], documents=documents)

    result = asyncio.run(aggregate_new_values(state, _config()))

    updated_values = result["clusters"][0][0]["values"]
    assert len(updated_values) == 1
    assert updated_values[0]["status"] == "accepted"
    assert updated_values[0]["label"] == "Store credit only"

    # Also check the delta_summary path used no LLM/embedding surprises.
    assert result["delta_summary"]["new_values"][0]["value"] == "Store credit only"
