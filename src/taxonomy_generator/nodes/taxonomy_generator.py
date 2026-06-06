"""Node for generating taxonomies from document batches."""

import logging
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model, parse_taxa, invoke_taxonomy_chain
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import TAXONOMY_GENERATION_PROMPT

logger = logging.getLogger(__name__)

def _setup_taxonomy_chain(configuration: Configuration, feedback: str):
    """Set up the chain for taxonomy generation."""
    # Initialize the prompt with default use case
    taxonomy_prompt = TAXONOMY_GENERATION_PROMPT.partial(
        use_case="Generate the taxonomy that can be used to label the user intent in the conversation.",
        feedback=feedback,
    )
    # Create the chain
    model = load_chat_model(
        configuration.fast_llm,
    )

    return (
        taxonomy_prompt
        | model
        | StrOutputParser()
        | parse_taxa
    ).with_config(run_name="GenerateTaxonomy")


async def generate_taxonomy(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Generate taxonomy from the first batch of documents."""
    configuration = Configuration.from_runnable_config(config)

    # Format the feedback if it exists
    feedback = "No previous feedback provided."
    if state.user_feedback:
        feedback = f"Previous user feedback: {state.user_feedback.feedback}"
        if state.user_feedback.explanation:
            feedback += f"\nReason for modification: {state.user_feedback.explanation}"
    
    logger.info("Generating initial taxonomy from first minibatch (%d documents)", len(state.minibatches[0]))

    # Set up the chain
    taxonomy_chain = _setup_taxonomy_chain(configuration, feedback)

    # Generate taxonomy using the first batch
    result = await invoke_taxonomy_chain(
        taxonomy_chain,
        state,
        config,
        state.minibatches[0],
    )
    num_clusters = len(result.get("clusters", [[]])[0]) if result.get("clusters") else 0
    logger.info("Initial taxonomy generated with %d categories", num_clusters)
    return result
