"""Node for reviewing and finalizing taxonomies."""

import logging
import random
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model, parse_taxa, invoke_taxonomy_chain
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import TAXONOMY_REVIEW_PROMPT

logger = logging.getLogger(__name__)


def _setup_review_chain(configuration: Configuration):
    """Set up the chain for taxonomy review.
    
    Args:
        model_name: Name of the model to use
        max_tokens: Maximum tokens for model response
        
    Returns:
        Chain for reviewing and parsing taxonomies
    """
    # Initialize the prompt
    review_prompt = TAXONOMY_REVIEW_PROMPT

    # Create the chain
    model = load_chat_model(configuration.fast_llm)

    return (
        review_prompt
        | model
        | StrOutputParser()
        | parse_taxa
    ).with_config(run_name="ReviewTaxonomy")


async def review_taxonomy(
    state: State,
    config: RunnableConfig
) -> dict:
    """Review and finalize taxonomy using a random sample of documents.
    
    Args:
        state: Current application state
        config: Configuration for the run
        model_name: Name of the model to use
        max_tokens: Maximum tokens for model response
        
    Returns:
        dict: Updated state fields with reviewed taxonomy
    """
    configuration = Configuration.from_runnable_config(config)
    
    # Set up the chain
    review_chain = _setup_review_chain(configuration)

    # Create random sample of documents
    batch_size = configuration.batch_size
    indices = list(range(len(state.documents)))
    random.shuffle(indices)
    sample_indices = indices[:batch_size]
    logger.info(
        "Reviewing taxonomy — sampling %d documents from %d (model: %s)",
        len(sample_indices), len(state.documents), configuration.fast_llm,
    )

    # Review taxonomy using sampled documents
    result = await invoke_taxonomy_chain(
        review_chain,
        state,
        config,
        sample_indices,
    )
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Taxonomy review complete — %d categories finalized", num_clusters)
    return result
