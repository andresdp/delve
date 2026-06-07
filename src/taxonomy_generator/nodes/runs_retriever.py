"""Node for accepting pre-populated documents and normalizing them.

Expects ``state.documents`` to already contain data (direct corpus input).
Normalizes them to Doc objects and returns them for downstream processing.
"""

import logging
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State, Doc
from taxonomy_generator.utils import docs_from_dicts

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

    normalized = docs_from_dicts(state.documents)
    status_message = f"Using {len(normalized)} documents (direct corpus input)."
    logger.info("Direct corpus mode: %d documents passed through", len(normalized))
    return {
        "all_documents": normalized,
        "documents": normalized,
        "status": [status_message],
    }