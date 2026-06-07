"""Route model output to the next node in the graph."""

import logging
from typing import Literal

from taxonomy_generator.state import State

logger = logging.getLogger(__name__)

def should_review(state: State) -> Literal["update_taxonomy", "review_taxonomy"]:
    """Determine whether to continue updating or move to review."""
    num_minibatches = len(state.minibatches)
    num_revisions = len(state.clusters)
    if num_revisions < num_minibatches:
        logger.info("Routing to update_taxonomy — revision %d of %d minibatches", num_revisions, num_minibatches)
        return "update_taxonomy"
    logger.info("Routing to review_taxonomy — all %d minibatches processed", num_minibatches)
    return "review_taxonomy"
