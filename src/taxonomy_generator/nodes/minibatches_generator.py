"""Node for generating minibatches from documents."""

import logging
import random
from typing import List

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.state import State
from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)


def _create_batches(indices: List[int], batch_size: int) -> List[List[int]]:
    """Create batches of document indices.

    Args:
        indices: List of document indices to batch
        batch_size: Size of each batch

    Returns:
        List of batches, where each batch is a list of document indices.
        The final batch may be smaller than ``batch_size`` if the total
        number of indices is not evenly divisible.

    Raises:
        ValueError: If ``batch_size`` is not a positive integer.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be a positive integer, got {batch_size}")

    if not indices:
        return []

    num_full_batches = len(indices) // batch_size
    batches = [
        indices[i * batch_size : (i + 1) * batch_size]
        for i in range(num_full_batches)
    ]

    leftovers = len(indices) % batch_size
    if leftovers:
        batches.append(indices[num_full_batches * batch_size :])

    return batches


async def generate_minibatches(state: State, config: RunnableConfig) -> dict:
    """Generate minibatches from documents for processing.

    Uses the global RNG state (already seeded by upstream nodes such as
    ``load_corpus`` when ``random_seed`` is configured).

    Args:
        state: Current application state
        config: Configuration for the run

    Returns:
        dict: Updated state fields with minibatches

    Raises:
        ValueError: If ``batch_size`` is not a positive integer.
    """
    if not state.documents:
        logger.warning("No documents to batch — returning empty minibatches.")
        return {
            "minibatches": [],
            "status": ["No documents to batch."],
        }

    configuration = Configuration.from_runnable_config(config)

    if configuration.batch_size <= 0:
        raise ValueError(
            f"batch_size must be a positive integer, got {configuration.batch_size}"
        )

    logger.info(
        "Generating minibatches from %d documents (batch_size: %d)",
        len(state.documents),
        configuration.batch_size,
    )

    # Shuffle document indices using the current global RNG state
    indices = list(range(len(state.documents)))
    random.shuffle(indices)

    # Generate batches
    batches = _create_batches(indices, configuration.batch_size)
    logger.info(
        "Created %d minibatches from %d documents", len(batches), len(state.documents)
    )

    return {
        "minibatches": batches,
        "status": ["Minibatches generated successfully."],
    }
