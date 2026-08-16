"""Route model output to the next node in the graph."""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_review(
    state: State,
    config: RunnableConfig,
) -> Literal["open_code_minibatch", "review_taxonomy"]:
    """Determine whether to keep updating or move to review.

    Routes to ``review_taxonomy`` once the saturation streak reaches the
    configured threshold **or** all minibatches have been processed,
    whichever comes first. If the minibatches exhaust without ever
    saturating, review proceeds anyway (the run simply completes
    unsaturated — visible in ``saturation_history``).

    The loop continues through ``open_code_minibatch`` so each new batch
    is open-coded before the next axial-coding update.
    """
    configuration = Configuration.from_runnable_config(config)

    num_minibatches = len(state.minibatches)
    num_revisions = len(state.clusters)
    saturated = state.saturation_streak >= configuration.saturation_streak_threshold

    if saturated:
        logger.info(
            "Routing to review_taxonomy — saturation streak %d reached threshold %d after %d revisions",
            state.saturation_streak, configuration.saturation_streak_threshold, num_revisions,
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

    logger.info(
        "Routing to open_code_minibatch — revision %d of %d minibatches (saturation streak %d/%d)",
        num_revisions, num_minibatches, state.saturation_streak, configuration.saturation_streak_threshold,
    )
    return "open_code_minibatch"