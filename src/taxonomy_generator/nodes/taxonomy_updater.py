"""Node for updating taxonomies based on new document batches."""

import logging

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import TAXONOMY_UPDATE_PROMPT
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import (
    format_feedback,
    invoke_taxonomy_chain,
    load_chat_model,
)
from taxonomy_generator.visualization import render_taxonomy_biplot

logger = logging.getLogger(__name__)


def _setup_update_chain(configuration: Configuration, feedback: str):
    """Set up the chain for taxonomy updates."""
    update_prompt = TAXONOMY_UPDATE_PROMPT.partial(
        use_case=configuration.use_case,
        feedback=feedback,
    )
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
    """Update taxonomy using the batch of documents just open-coded."""
    configuration = Configuration.from_runnable_config(config)

    feedback = format_feedback(state)

    update_chain = _setup_update_chain(configuration, feedback)

    # Open coding has already advanced past the current batch, so the batch
    # to axially incorporate is at (open_code_batch_index - 1). This matches
    # the pre-existing schedule (first update = second minibatch, etc.).
    which_mb = max(state.open_code_batch_index - 1, 0)
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

    # Optional per-iteration biplot of the evolving draft values.
    if result.get("clusters"):
        await render_taxonomy_biplot(
            configuration, result["clusters"][0], stage="update",
            iteration_index=len(state.clusters) + 1,
        )

    return result