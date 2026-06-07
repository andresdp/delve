"""Routing logic for the summarization step."""

import logging
from typing import Literal

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State

logger = logging.getLogger(__name__)


def should_summarize(
    state: State,
    config: RunnableConfig,
) -> Literal["summarize", "get_minibatches"]:
    """Determine whether to summarize documents or skip to minibatch generation.

    When ``skip_summarization`` is ``True``, documents pass through without
    LLM-generated summaries and raw content is used for taxonomy generation
    instead.
    """
    configuration = Configuration.from_runnable_config(config)

    if configuration.skip_summarization:
        logger.warning(
            "Summarization is disabled (skip_summarization=true). "
            "Raw document content will be used for taxonomy generation. "
            "This may reduce taxonomy quality for long documents."
        )
        return "get_minibatches"

    return "summarize"