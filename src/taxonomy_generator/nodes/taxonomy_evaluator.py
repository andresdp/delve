"""Observe-only taxonomy evaluation node.

Runs the deepeval scoreboard over the run's effective taxonomy view — train
mode scores the final (post-selection) view; test mode scores the frozen
seeded taxonomy against the new corpus documents as a drift signal. The
node returns only ``{"evaluation": scoreboard, "status": [...]}``; it never
writes clusters, selected_clusters, or routing-relevant state, and an
evaluation failure degrades to the unavailable scoreboard without failing
the run.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation.runner import run_scoreboard
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def _resolve_view(state: State, mode: str) -> List[Dict]:
    """Resolve the taxonomy view to evaluate for the given run mode."""
    if mode == "test":
        # The frozen seed (possibly value-extended by aggregation later).
        return list(state.clusters[-1]) if state.clusters else []
    # Train: the selected view when dimension selection ran, else the last.
    if state.selected_clusters:
        return list(state.selected_clusters[-1])
    return list(state.clusters[-1]) if state.clusters else []


async def evaluate_taxonomy(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Evaluate the run's taxonomy view (observe-only)."""
    configuration = Configuration.from_runnable_config(config)

    if not configuration.evaluation_enabled:
        logger.debug("Evaluation disabled — skipping evaluate_taxonomy.")
        return {
            "evaluation": None,
            "status": ["Evaluation disabled (evaluation.enabled: false)."],
        }

    view = _resolve_view(state, configuration.mode)
    if not view:
        logger.warning("No taxonomy view to evaluate — skipping evaluation.")
        return {
            "evaluation": None,
            "status": ["Evaluation skipped — no taxonomy view available."],
        }

    documents: List[object] = list(state.documents or [])[
        : configuration.evaluation_max_documents
    ]
    mode_label = "frozen seed (drift)" if configuration.mode == "test" else "final view"
    logger.info(
        "Evaluating taxonomy (%s, %d dimensions, %d sampled documents)",
        mode_label, len(view), len(documents),
    )

    scoreboard = await run_scoreboard(view, documents, configuration)
    if scoreboard.get("unavailable"):
        logger.warning("Taxonomy evaluation unavailable: %s", scoreboard.get("error"))

    return {
        "evaluation": scoreboard,
        "status": [f"Evaluated taxonomy ({mode_label})."],
    }