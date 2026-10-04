"""Node for reviewing and finalizing taxonomies."""

import logging
import random

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import (
    TAXONOMY_REVIEW_PROMPT,
    TAXONOMY_REVIEW_TOOLS_PROMPT,
)
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.state import State
from taxonomy_generator.tool_update import restore_after_rewrite, tool_mode_node
from taxonomy_generator.utils import (
    format_feedback,
    invoke_taxonomy_chain,
    load_chat_model,
)
from taxonomy_generator.visualization import render_taxonomy_biplot

logger = logging.getLogger(__name__)


def _setup_review_chain(configuration: Configuration, feedback: str):
    """Set up the chain for taxonomy review."""
    review_prompt = TAXONOMY_REVIEW_PROMPT.partial(
        use_case=configuration.use_case,
        feedback=feedback,
    )
    model = load_chat_model(configuration.generation_llm)
    structured_model = model.with_structured_output(TaxonomyOutput)

    return (
        review_prompt
        | structured_model
    ).with_config(run_name="ReviewTaxonomy")


async def review_taxonomy(
    state: State,
    config: RunnableConfig
) -> dict:
    """Review and finalize taxonomy using a random sample of documents.

    ``taxonomy.edit_mode`` picks how, as in ``update_taxonomy``; in tools mode the
    review sample's documents are the evidence the operations may cite.
    """
    configuration = Configuration.from_runnable_config(config)

    feedback = format_feedback(state, configuration.evaluation_feedback_exclude or ())

    review_size = configuration.review_sample_size or configuration.batch_size
    indices = list(range(len(state.documents)))
    random.shuffle(indices)
    sample_indices = indices[:review_size]
    edit_mode = configuration.edit_mode or "rewrite"
    logger.info(
        "Reviewing taxonomy — sampling %d documents from %d (model: %s, edit mode: %s)",
        len(sample_indices), len(state.documents), configuration.generation_llm, edit_mode,
    )

    if edit_mode == "tools":
        prompt = TAXONOMY_REVIEW_TOOLS_PROMPT.partial(use_case=configuration.use_case, feedback=feedback)
        result = await tool_mode_node(load_chat_model(configuration.generation_llm), prompt, state, config,
                                      configuration, sample_indices, node="review_taxonomy", review=True)
    else:
        review_chain = _setup_review_chain(configuration, feedback)
        result = await invoke_taxonomy_chain(
            review_chain,
            state,
            config,
            sample_indices,
        )
        if edit_mode == "rewrite_restore":
            result = restore_after_rewrite(result, state, node="review_taxonomy")
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Taxonomy review complete — %d categories finalized", num_clusters)

    # Optional biplot of the post-polish draft values.
    if result.get("clusters"):
        await render_taxonomy_biplot(
            configuration, result["clusters"][0], stage="review",
            iteration_index=len(state.clusters) + 1,
        )

    return result
