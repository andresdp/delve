"""Regression tests for biplot filename iteration numbering.

Every node that appends its own result to ``state.clusters`` (an
``Annotated[List, operator.add]`` field — accumulation happens only after
the node returns, so ``state.clusters`` as read inside the node is always
one short of the final count) must pass ``iteration_index=len(state.clusters)
+ 1`` to ``render_taxonomy_biplot``, matching the position its own result
will occupy once appended. ``taxonomy_generator.py`` (stage "generate") is
exempt: it is always the first entry, hardcoded to ``iteration_index=1``.

Getting this wrong desyncs the biplot filename from the final taxonomy
JSON's ``iterations`` length that ``html_report.discover_siblings`` /
``resolve_biplot_path`` key their lookup on — the report then renders "No
biplot is available for this run" even though a biplot file exists on disk,
just under the wrong iteration number.
"""

import asyncio
from unittest.mock import AsyncMock, patch

from taxonomy_generator.nodes import (
    taxonomy_reviewer,
    taxonomy_updater,
    value_consolidator,
)
from taxonomy_generator.state import State


def _config(**overrides) -> dict:
    configurable = {
        "mode": "train",
        "visualization_enabled": True,
        "visualization_every_iteration": True,
        **overrides,
    }
    return {"configurable": configurable}


def _doc(doc_id: str) -> dict:
    return {"id": doc_id, "content": f"content {doc_id}", "summary": f"summary {doc_id}"}


def test_update_taxonomy_biplot_iteration_index_anticipates_own_append():
    """Existing-correct behavior, pinned as a regression guard."""
    state = State(
        documents=[_doc("d1"), _doc("d2")],
        clusters=[[{"id": "1", "name": "A", "description": "d", "values": []}]],  # len 1
        minibatches=[[0], [1]],
        open_code_batch_index=2,
    )
    fake_result = {"clusters": [[{"id": "1", "name": "A", "description": "d", "values": []}]]}

    with patch.object(taxonomy_updater, "invoke_taxonomy_chain", new=AsyncMock(return_value=fake_result)), \
         patch.object(taxonomy_updater, "render_taxonomy_biplot", new=AsyncMock(return_value=None)) as mock_render:
        asyncio.run(taxonomy_updater.update_taxonomy(state, _config()))

    assert mock_render.call_args.kwargs["iteration_index"] == len(state.clusters) + 1 == 2


def test_review_taxonomy_biplot_iteration_index_anticipates_own_append():
    state = State(
        documents=[_doc("d1"), _doc("d2")],
        clusters=[
            [{"id": "1", "name": "A", "description": "d", "values": []}],
            [{"id": "1", "name": "A", "description": "d", "values": []}],
        ],  # len 2 (generate + update already ran)
    )
    fake_result = {"clusters": [[{"id": "1", "name": "A", "description": "d", "values": []}]]}

    with patch.object(taxonomy_reviewer, "invoke_taxonomy_chain", new=AsyncMock(return_value=fake_result)), \
         patch.object(taxonomy_reviewer, "render_taxonomy_biplot", new=AsyncMock(return_value=None)) as mock_render:
        asyncio.run(taxonomy_reviewer.review_taxonomy(state, _config()))

    assert mock_render.call_args.kwargs["iteration_index"] == len(state.clusters) + 1 == 3


def test_consolidate_values_disabled_path_biplot_iteration_index_anticipates_own_append():
    state = State(
        clusters=[
            [{"id": "1", "name": "A", "description": "d", "values": []}],
            [{"id": "1", "name": "A", "description": "d", "values": []}],
            [{"id": "1", "name": "A", "description": "d", "values": []}],
        ],  # len 3 (generate + update + review already ran)
    )

    with patch.object(value_consolidator, "render_taxonomy_biplot", new=AsyncMock(return_value=None)) as mock_render:
        asyncio.run(value_consolidator.consolidate_values(state, _config(consolidate_values=False)))

    assert mock_render.call_args.kwargs["iteration_index"] == len(state.clusters) + 1 == 4


def test_consolidate_values_normal_path_biplot_iteration_index_anticipates_own_append():
    values = [
        {"id": "1.1", "dimension_id": "1", "label": "v1", "description": "d1", "status": "accepted"},
        {"id": "1.2", "dimension_id": "1", "label": "v2", "description": "d2", "status": "accepted"},
        {"id": "1.3", "dimension_id": "1", "label": "v3", "description": "d3", "status": "accepted"},
    ]
    state = State(
        clusters=[
            [{"id": "1", "name": "A", "description": "d", "values": []}],
            [{"id": "1", "name": "A", "description": "d", "values": []}],
            [{"id": "1", "name": "A", "description": "d", "values": values}],
        ],  # len 3 (generate + update + review already ran)
    )

    class _FakeEmbeddings:
        async def aembed_documents(self, texts):
            # Three well-separated 2D unit vectors so the >=3-points floor
            # in render_taxonomy_biplot's caller path is met and no merges
            # complicate the resulting value count.
            return [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]]

    with patch.object(value_consolidator, "render_taxonomy_biplot", new=AsyncMock(return_value=None)) as mock_render, \
         patch.object(value_consolidator, "load_embeddings_model", return_value=_FakeEmbeddings()):
        asyncio.run(value_consolidator.consolidate_values(state, _config(consolidate_values=True)))

    assert mock_render.call_args.kwargs["iteration_index"] == len(state.clusters) + 1 == 4
