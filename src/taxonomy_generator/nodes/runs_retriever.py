"""Node for accepting pre-populated documents and normalizing them.

Expects ``state.documents`` to already contain data (direct corpus input).
Normalizes them to Doc objects, then applies ``max_runs`` and ``sample_size``
limits from the configuration.
"""

import logging
import random
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State, Doc
from taxonomy_generator.utils import docs_from_dicts
from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)


async def retrieve_runs(state: State, config: RunnableConfig) -> dict:
    """Normalize pre-populated documents for the pipeline.

    Expects ``state.documents`` to contain data provided via direct corpus
    input (e.g. ``--corpus`` flag on the CLI). Converts them to Doc objects
    and returns them.

    Args:
        state: Current application state
        config: Configuration for the run

    Returns:
        dict: Updated state fields with documents

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
    normalized = docs_from_dicts(state.documents)

    # Apply max_runs cap (0 = no limit)
    if configuration.max_runs > 0 and len(normalized) > configuration.max_runs:
        logger.info("Capping documents from %d to max_runs=%d", len(normalized), configuration.max_runs)
        normalized = normalized[:configuration.max_runs]

    # Apply sample_size sampling (0 = use all)
    if configuration.sample_size > 0 and len(normalized) > configuration.sample_size:
        if configuration.random_seed is not None:
            random.seed(configuration.random_seed)
        logger.info("Sampling %d documents from %d (sample_size=%d)", configuration.sample_size, len(normalized), configuration.sample_size)
        normalized = random.sample(normalized, configuration.sample_size)

    status_message = f"Using {len(normalized)} documents (direct corpus input)."
    logger.info("Direct corpus mode: %d documents passed through", len(normalized))
    return {
        "all_documents": normalized,
        "documents": normalized,
        "status": [status_message],
    }
