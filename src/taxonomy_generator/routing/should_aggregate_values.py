"""Routing logic after labeling: aggregate new values (test mode) or finish."""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_aggregate_values(
    state: State,
    config: RunnableConfig,
) -> Literal["evaluate_taxonomy", "aggregate_new_values", "__end__"]:
    """Route to test-mode evaluation/aggregation or end the run.

    In ``test`` mode, labeled documents may carry proposed new values; the
    aggregation node deduplicates and appends them to the frozen dimensions
    and emits the delta summary. When evaluation is enabled, test mode first
    routes through the observe-only evaluator (frozen seed vs. the new
    corpus, a drift signal) before aggregating. In ``train`` mode the run is
    complete once documents are labeled.
    """
    configuration = Configuration.from_runnable_config(config)

    if configuration.mode == "test":
        if configuration.evaluation_enabled:
            return "evaluate_taxonomy"
        return "aggregate_new_values"

    return "__end__"