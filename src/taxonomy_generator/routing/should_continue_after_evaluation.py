"""Routing logic around the observe-only evaluation node.

``should_continue_after_evaluation`` routes by run mode after the scoreboard
runs. ``should_evaluate_after_selection`` routes after dimension selection:
evaluate the final view (enabled) or label directly (disabled — today's
topology).
"""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_continue_after_evaluation(
    state: State,
    config: RunnableConfig,
) -> Literal["label_documents", "aggregate_new_values"]:
    """Route after the evaluate_taxonomy node by run mode."""
    configuration = Configuration.from_runnable_config(config)

    if configuration.mode == "test":
        return "aggregate_new_values"

    return "label_documents"


def should_evaluate_after_selection(
    state: State,
    config: RunnableConfig,
) -> Literal["evaluate_taxonomy", "label_documents"]:
    """Route after dimension selection: evaluate the final view or label directly."""
    configuration = Configuration.from_runnable_config(config)

    if configuration.evaluation_enabled:
        return "evaluate_taxonomy"

    return "label_documents"