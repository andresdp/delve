"""Node for generating taxonomies from document batches."""

import logging

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import TAXONOMY_GENERATION_PROMPT
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import (
    format_feedback,
    invoke_taxonomy_chain,
    load_chat_model,
)
from taxonomy_generator.visualization import embed_and_render

logger = logging.getLogger(__name__)

def _setup_taxonomy_chain(configuration: Configuration, feedback: str):
    """Set up the chain for taxonomy generation."""
    taxonomy_prompt = TAXONOMY_GENERATION_PROMPT.partial(
        use_case=configuration.use_case,
        feedback=feedback,
    )
    model = load_chat_model(configuration.model)
    structured_model = model.with_structured_output(TaxonomyOutput)

    return (
        taxonomy_prompt
        | structured_model
    ).with_config(run_name="GenerateTaxonomy")


async def generate_taxonomy(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Generate taxonomy from the first batch of documents (axial coding)."""
    configuration = Configuration.from_runnable_config(config)

    # NOTE: Feedback for the initial taxonomy must come from external sources —
    # either pre-populated in the initial state or injected via human-in-the-loop.
    # In the standard pipeline flow, no feedback is available at this stage.
    feedback = format_feedback(state)
    logger.info("Generating initial taxonomy from first minibatch (%d documents)", len(state.minibatches[0]))

    taxonomy_chain = _setup_taxonomy_chain(configuration, feedback)

    result = await invoke_taxonomy_chain(
        taxonomy_chain,
        state,
        config,
        state.minibatches[0],
    )
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Initial taxonomy generated with %d categories", num_clusters)

    # Optional per-iteration PCA chart of the draft values.
    if result.get("clusters"):
        await embed_and_render(
            configuration, result["clusters"][0], stage="generate", iteration_index=1,
        )

    return result