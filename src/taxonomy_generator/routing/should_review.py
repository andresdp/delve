"""Route model output to the next node in the graph."""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def coded_fraction(state: State) -> float:
    """Share of the corpus's documents in the minibatches open-coded so far."""
    total = sum(len(mb) for mb in state.minibatches)
    if total == 0:
        return 1.0
    coded = sum(len(mb) for mb in state.minibatches[: state.open_code_batch_index])
    return coded / total


def should_review(
    state: State,
    config: RunnableConfig,
) -> Literal["open_code_minibatch", "review_taxonomy"]:
    """Determine whether to keep updating or move to review.

    Routes to ``review_taxonomy`` once the saturation streak reaches the
    configured threshold **and** at least ``saturation_min_corpus_fraction``
    of the corpus's documents have been open-coded, **or** once all
    minibatches have been processed, whichever comes first. If the
    minibatches exhaust without ever saturating, review proceeds anyway (the
    run simply completes unsaturated — visible in ``saturation_history``).

    The minimum fraction guards against stopping on a few random batches that
    happen to agree: saturation reached earlier is recorded in
    ``saturation_history`` but does not end the loop, and it must still hold
    (an unbroken streak) once the minimum is reached.

    The loop continues through ``open_code_minibatch`` so each new batch
    is open-coded before the next axial-coding update.
    """
    configuration = Configuration.from_runnable_config(config)

    num_minibatches = len(state.minibatches)
    num_revisions = len(state.clusters)
    saturated = state.saturation_streak >= configuration.saturation_streak_threshold
    min_fraction = configuration.saturation_min_corpus_fraction or 0.0
    fraction = coded_fraction(state)

    if saturated and fraction >= min_fraction:
        logger.info(
            "Routing to review_taxonomy — saturation streak %d reached threshold %d after %d revisions "
            "(%.0f%% of documents open-coded)",
            state.saturation_streak, configuration.saturation_streak_threshold, num_revisions, fraction * 100,
        )
        return "review_taxonomy"

    if num_revisions >= num_minibatches:
        if not saturated:
            logger.info(
                "Minibatches exhausted without saturation (streak %d/%d) — proceeding to review_taxonomy",
                state.saturation_streak, configuration.saturation_streak_threshold,
            )
        else:
            logger.info("Routing to review_taxonomy — all %d minibatches processed", num_minibatches)
        return "review_taxonomy"

    if saturated:
        logger.info(
            "Saturation reached, but only %.0f%% of documents open-coded (minimum %.0f%%) — continuing",
            fraction * 100, min_fraction * 100,
        )
    logger.info(
        "Routing to open_code_minibatch — revision %d of %d minibatches (saturation streak %d/%d)",
        num_revisions, num_minibatches, state.saturation_streak, configuration.saturation_streak_threshold,
    )
    return "open_code_minibatch"
