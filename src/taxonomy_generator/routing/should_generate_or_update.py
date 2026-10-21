"""Routing logic after open coding: initial generation vs. incremental update."""

import logging
from typing import Literal

from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_generate_or_update(state: State) -> Literal["generate_taxonomy", "update_taxonomy"]:
    """Route to initial generation or incremental update after open coding.

    The first open-coding pass (no taxonomy yet) feeds ``generate_taxonomy``;
    every later pass feeds ``update_taxonomy``.
    """
    if not state.clusters:
        logger.debug("Routing to generate_taxonomy — no taxonomy yet")
        return "generate_taxonomy"
    logger.debug("Routing to update_taxonomy — taxonomy exists (%d iterations)", len(state.clusters))
    return "update_taxonomy"