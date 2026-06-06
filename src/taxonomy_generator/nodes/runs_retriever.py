"""Node for retrieving runs from LangSmith or accepting pre-populated documents.

Supports two input modes:
1. **Direct corpus input**: If `state.documents` is already populated, the node
   acts as a passthrough, using the provided documents directly.
2. **LangSmith retrieval**: If `state.documents` is empty and `project_name` is
   set, the node fetches conversation runs from LangSmith.
"""

import logging
from datetime import datetime, timedelta
from langsmith import Client, traceable
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State, Doc
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.utils import process_runs, docs_from_dicts

logger = logging.getLogger(__name__)


@traceable
async def retrieve_runs(state: State, config: RunnableConfig) -> dict:
    """Retrieve and process runs from LangSmith, or pass through pre-populated documents.

    If `state.documents` already contains data (direct corpus input mode), this
    node normalizes them to Doc objects and returns them without contacting LangSmith.
    Otherwise, it falls back to LangSmith retrieval using `project_name`, `org_id`,
    and `days`.

    Args:
        state: Current application state
        config: Configuration for the run

    Returns:
        dict: Updated state fields with documents

    Raises:
        ValueError: If neither documents nor project_name are provided
    """

    # --- Direct corpus input mode (passthrough) ---
    if state.documents:
        normalized = docs_from_dicts(state.documents)
        status_message = f"Using {len(normalized)} pre-populated documents (direct corpus input)."
        logger.info("Direct corpus mode: %d documents passed through", len(normalized))
        return {
            "all_documents": normalized,
            "documents": normalized,
            "status": [status_message],
        }

    # --- LangSmith retrieval mode (legacy) ---
    if not state.project_name:
        logger.error("No documents provided and project_name is not set")
        raise ValueError(
            "No documents provided and project_name is not set. "
            "Either pass a list of documents via the 'documents' field, "
            "or provide 'project_name', 'org_id', and 'days' for LangSmith retrieval."
        )

    configuration = Configuration.from_runnable_config(config)
    logger.info("LangSmith retrieval mode — project: %s, lookback: %d days", state.project_name, state.days)

    client = Client(api_key=state.org_id)

    delta_days = datetime.now() - timedelta(days=state.days)

    runs = list(
        client.list_runs(
            project_name=state.project_name,
            filter="eq(is_root, true)",
            start_time=delta_days,
            select=["inputs", "outputs"],
            limit=configuration.max_runs,
        )
    )

    if len(runs) == configuration.max_runs:
        status_message = f"Fetched runs were capped at {configuration.max_runs} due to the set limit."
        logger.warning("Runs capped at %d (max_runs limit reached)", configuration.max_runs)
    else:
        status_message = f"Fetched {len(runs)} runs successfully..."
        logger.info("Fetched %d runs from LangSmith", len(runs))

    all_docs = process_runs(left=[], right=runs)
    sampled_docs = process_runs(left=[], right=runs, sample=configuration.sample_size)
    logger.info("Processed %d total documents, sampled %d for taxonomy generation", len(all_docs), len(sampled_docs))

    return {
        "all_documents": all_docs,
        "documents": sampled_docs,
        "status": [status_message],
    }
