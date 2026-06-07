"""Node for loading and normalizing a document corpus.

Expects ``state.documents`` to already contain data (direct corpus input
via the ``--corpus`` CLI flag). Normalizes them to ``Doc`` objects, then
applies ``max_runs`` and ``sample_size`` limits from the configuration.
"""

import logging
import random

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State, Doc
from taxonomy_generator.utils import docs_from_dicts
from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)


async def load_corpus(state: State, config: RunnableConfig) -> dict:
    """Normalize pre-populated documents for the pipeline.

    Expects ``state.documents`` to contain data provided via direct corpus
    input (e.g. ``--corpus`` flag on the CLI). Converts them to ``Doc``
    objects, applies capping and sampling, and returns the working set.

    Args:
        state: Current application state
        config: Configuration for the run

    Returns:
        dict: Updated state fields with documents and status

    Raises:
        ValueError: If no documents are provided
    """
    if not state.documents:
        logger.error("No documents provided")
        raise ValueError(
            "No documents provided. "
            "Pass a list of documents via the 'documents' field "
            "(e.g. use the --corpus flag on the CLI)."
        )

    configuration = Configuration.from_runnable_config(config)

    # Log effective configuration
    logger.info(
        "Corpus loader config: max_runs=%d, sample_size=%d, random_seed=%s",
        configuration.max_runs,
        configuration.sample_size,
        configuration.random_seed,
    )

    normalized = docs_from_dicts(state.documents)
    original_count = len(normalized)

    # Apply max_runs cap (0 = no limit), with optional shuffle
    if configuration.max_runs > 0 and len(normalized) > configuration.max_runs:
        if configuration.random_seed is not None:
            random.seed(configuration.random_seed)
        random.shuffle(normalized)
        normalized = normalized[:configuration.max_runs]
        logger.info(
            "Capped documents from %d to max_runs=%d (shuffled before capping)",
            original_count,
            configuration.max_runs,
        )

    # Apply sample_size sampling (0 = use all)
    if configuration.sample_size > 0 and len(normalized) > configuration.sample_size:
        if configuration.random_seed is not None:
            random.seed(configuration.random_seed)
        logger.info(
            "Sampling %d documents from %d (sample_size=%d)",
            configuration.sample_size,
            len(normalized),
            configuration.sample_size,
        )
        normalized = random.sample(normalized, configuration.sample_size)

    status_message = f"Using {len(normalized)} documents (direct corpus input)."
    logger.info("Corpus loaded: %d documents (original: %d)", len(normalized), original_count)
    return {
        "documents": normalized,
        "status": [status_message],
    }