"""Routing logic after corpus load: summarize, skip, or label (test mode)."""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_summarize(
    state: State,
    config: RunnableConfig,
) -> Literal["summarize", "get_minibatches", "label_documents"]:
    """Route after corpus load.

    Three outcomes:

    - ``test`` mode classifies directly against the seeded frozen taxonomy —
      summarization and minibatching are skipped because the labeler reads raw
      document content and no taxonomy refinement happens in this mode.
    - ``train`` mode (default) keeps the existing two-way behavior: skip
      summarization when ``skip_summarization`` is true, else summarize.
    """
    configuration = Configuration.from_runnable_config(config)

    if configuration.mode == "test":
        logger.info("Test mode: routing directly to document labeling")
        return "label_documents"

    if configuration.skip_summarization:
        logger.warning(
            "Summarization is disabled (skip_summarization=true). "
            "Raw document content will be used for taxonomy generation. "
            "This may reduce taxonomy quality for long documents."
        )
        return "get_minibatches"

    return "summarize"