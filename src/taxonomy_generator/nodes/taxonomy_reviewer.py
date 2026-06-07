"""Node for reviewing and finalizing taxonomies."""

import logging
import random
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model, invoke_taxonomy_chain
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.prompts import TAXONOMY_REVIEW_PROMPT

logger = logging.getLogger(__name__)


def _setup_review_chain(configuration: Configuration):
    """Set up the chain for taxonomy review."""
    review_prompt = TAXONOMY_REVIEW_PROMPT
    model = load_chat_model(configuration.model)
    structured_model = model.with_structured_output(TaxonomyOutput)

    return (
        review_prompt
        | structured_model
    ).with_config(run_name="ReviewTaxonomy")


async def review_taxonomy(
    state: State,
    config: RunnableConfig
) -> dict:
    """Review and finalize taxonomy using a random sample of documents."""
    configuration = Configuration.from_runnable_config(config)
    
    review_chain = _setup_review_chain(configuration)

    review_size = configuration.review_sample_size or configuration.batch_size
    indices = list(range(len(state.documents)))
    random.shuffle(indices)
    sample_indices = indices[:review_size]
    logger.info(
        "Reviewing taxonomy — sampling %d documents from %d (model: %s)",
        len(sample_indices), len(state.documents), configuration.model,
    )

    result = await invoke_taxonomy_chain(
        review_chain,
        state,
        config,
        sample_indices,
    )
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Taxonomy review complete — %d categories finalized", num_clusters)
    return result