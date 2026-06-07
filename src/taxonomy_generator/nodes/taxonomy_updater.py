"""Node for updating taxonomies based on new document batches."""

import logging
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model, invoke_taxonomy_chain
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.prompts import TAXONOMY_UPDATE_PROMPT

logger = logging.getLogger(__name__)


def _setup_update_chain(configuration: Configuration):
    """Set up the chain for taxonomy updates."""
    update_prompt = TAXONOMY_UPDATE_PROMPT
    model = load_chat_model(configuration.model)
    structured_model = model.with_structured_output(TaxonomyOutput)

    return (
        update_prompt
        | structured_model
    ).with_config(run_name="UpdateTaxonomy")


async def update_taxonomy(
    state: State,
    config: RunnableConfig
) -> dict:
    """Update taxonomy using the next batch of documents."""
    configuration = Configuration.from_runnable_config(config)
    
    update_chain = _setup_update_chain(configuration)

    which_mb = len(state.clusters) % len(state.minibatches)
    mb_indices = state.minibatches[which_mb]
    logger.info(
        "Updating taxonomy — iteration %d, minibatch %d (%d documents), model: %s",
        len(state.clusters), which_mb, len(mb_indices), configuration.model,
    )

    result = await invoke_taxonomy_chain(
        update_chain,
        state,
        config,
        mb_indices,
    )
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Taxonomy updated — now %d categories", num_clusters)
    return result
