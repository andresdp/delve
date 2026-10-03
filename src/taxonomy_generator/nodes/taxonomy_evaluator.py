"""Observe-only taxonomy evaluation node.

Runs the deepeval scoreboard over the run's effective taxonomy view. This
node is wired into the graph at two call sites (see ``graph.py``):

- A **loop call** (train mode only), after every ``generate_taxonomy``/
  ``update_taxonomy`` pass, scoring the current in-progress draft — this is
  intentionally *not* the final view (``selected_clusters`` is empty until
  ``select_dimensions`` runs later), since its purpose is fresh per-iteration
  feedback for ``update_taxonomy``/``review_taxonomy`` via
  ``format_feedback``.
- A **final call**, after ``select_dimensions`` (train) or ``label_documents``
  (test), scoring the settled final view — train mode scores the selected
  view (or the last generated view, if selection didn't run); test mode
  scores the frozen seeded taxonomy against the new corpus documents as a
  drift signal. This call is always the chronologically last evaluator call
  in the run, so its scoreboard is what ends up in ``state.evaluation``.

The node returns ``{"evaluation": scoreboard, "evaluation_history": [...],
"status": [...]}`` from every call; each scoreboard records the ``view`` it
scored, the ``iteration`` (number of taxonomy snapshots so far) and the number
of ``dimensions``, and the run saves the whole history; it never writes clusters,
selected_clusters, or routing-relevant state, and an evaluation failure
degrades to the unavailable scoreboard without failing the run.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation.runner import run_scoreboard, sample_documents
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def _resolve_view(state: State, mode: str) -> List[Dict]:
    """Resolve the taxonomy view to evaluate for the given run mode.

    Train mode always resolves to ``clusters[-1]`` during the axial-coding
    loop (the loop call site) since ``selected_clusters`` is empty until
    ``select_dimensions`` runs later — that is the intended draft view for
    per-iteration feedback, not a gap. Once selection has run (the final
    call site), it resolves to the selected view instead.
    """
    if mode == "test":
        # The frozen seed (possibly value-extended by aggregation later).
        return list(state.clusters[-1]) if state.clusters else []
    # Train: the selected view when dimension selection ran, else the last.
    if state.selected_clusters:
        return list(state.selected_clusters[-1])
    return list(state.clusters[-1]) if state.clusters else []


def _skip_loop_draft(state: State, configuration: Configuration) -> bool:
    """Whether this loop call skips scoring (``evaluation.every_n_iterations``).

    Drafts 1, 1+N, 1+2N, … are scored, and so is the draft of the last
    minibatch (so review gets fresh feedback when the batches run out). The
    final call (after selection, or in test mode) is never skipped. A run
    that stops on saturation between scored drafts reviews without
    evaluation feedback, since feedback about an older draft would name ids
    and structure that no longer exist.
    """
    every = configuration.evaluation_every_n_iterations or 1
    if every <= 1 or configuration.mode == "test" or state.selected_clusters:
        return False
    if state.minibatches and state.open_code_batch_index >= len(state.minibatches):
        return False
    return (len(state.clusters) - 1) % every != 0


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
            "evaluation_history": [],
            "status": ["Evaluation disabled (evaluation.enabled: false)."],
        }

    if _skip_loop_draft(state, configuration):
        every = configuration.evaluation_every_n_iterations
        logger.info("Skipping evaluation of draft %d (scored every %d iterations)", len(state.clusters), every)
        return {
            "evaluation_history": [],
            "status": [f"Evaluation skipped for draft {len(state.clusters)} (every {every} iterations)."],
        }

    view = _resolve_view(state, configuration.mode)
    if not view:
        logger.warning("No taxonomy view to evaluate — skipping evaluation.")
        return {
            "evaluation": None,
            "evaluation_history": [],
            "status": ["Evaluation skipped — no taxonomy view available."],
        }

    # The same seeded, source-stratified sample at every call, so scores from
    # different iterations are judged on the same passages.
    documents: List[object] = sample_documents(
        list(state.documents or []),
        configuration.evaluation_max_documents,
        configuration.random_seed,
    )
    if configuration.mode == "test":
        mode_label = "frozen seed (drift)"
    elif state.selected_clusters:
        mode_label = "final view"
    else:
        mode_label = "loop draft, pre-selection"
    logger.info(
        "Evaluating taxonomy (%s, %d dimensions, %d sampled documents)",
        mode_label, len(view), len(documents),
    )

    scoreboard = await run_scoreboard(view, documents, configuration)
    if scoreboard.get("unavailable"):
        logger.warning("Taxonomy evaluation unavailable: %s", scoreboard.get("error"))
    # Which view was scored, so the saved history can be read per iteration:
    # loop drafts are the raw axial-coding output, the final view is the
    # consolidated and selected taxonomy (not directly comparable).
    scoreboard = {
        **scoreboard,
        "view": mode_label,
        "iteration": len(state.clusters),
        "dimensions": len(view),
    }

    return {
        "evaluation": scoreboard,
        "evaluation_history": [scoreboard],
        "status": [f"Evaluated taxonomy ({mode_label})."],
    }