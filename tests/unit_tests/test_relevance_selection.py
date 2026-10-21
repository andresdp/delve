"""taxonomy.relevance_selection: the LLM use-case relevance filter can be switched off (structural rules stay)."""

import asyncio
from unittest.mock import patch

import pytest

from taxonomy_generator.configuration import init_settings
from taxonomy_generator.nodes import dimension_selector
from taxonomy_generator.settings import load_settings
from taxonomy_generator.state import State


def _dim(dim_id, sources, candidates):
    values = [{"id": f"{dim_id}.{i}", "label": f"v{i}", "status": "accepted"} for i in range(1, candidates + 1)]
    return {"id": dim_id, "name": f"Dim {dim_id}", "description": "q", "values": values,
            "evidence": {"codes": 5, "documents": 5, "sources": sources}}


def _state():
    return State(clusters=[[_dim("1", 3, 2), _dim("2", 1, 3), _dim("3", 4, 1), _dim("4", 2, 2)]])


def _config(**overrides):
    return {"configurable": {"min_dimension_sources": 2, "min_candidate_decisions": 2, **overrides}}


def test_without_relevance_filter_every_structurally_valid_dimension_is_selected():
    with patch.object(dimension_selector, "load_chat_model", side_effect=AssertionError("no LLM call expected")):
        result = asyncio.run(dimension_selector.select_dimensions(_state(), _config(relevance_selection=False)))
    assert [c["id"] for c in result["selected_clusters"][0]] == ["1", "4"]
    assert {d["id"] for d in result["dropped_dimensions"]} == {"2", "3"}  # support and decision-point rules
    assert "relevance filter disabled" in result["explanations"][0]


def test_relevance_filter_is_on_by_default(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  name: t\n")
    assert load_settings(str(cfg)).taxonomy.relevance_selection is True


def test_relevance_selection_from_yaml(tmp_path):
    from taxonomy_generator.configuration import Configuration

    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  relevance_selection: false\n")
    try:
        init_settings(str(cfg))
        assert Configuration.from_runnable_config({"configurable": {}}).relevance_selection is False
    finally:
        init_settings(None)


def test_relevance_selection_must_be_a_boolean(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  relevance_selection: maybe\n")
    with pytest.raises(ValueError, match="relevance_selection"):
        load_settings(str(cfg))
