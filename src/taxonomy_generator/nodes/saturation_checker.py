"""Node for checking theoretical saturation of the taxonomy.

Runs after each ``update_taxonomy`` pass: compares the current minibatch's
open codes against the existing taxonomy and records whether they are
subsumed (saturated) or reveal uncovered concepts. Feeds its verdict back
into the existing feedback mechanism as an automated critic.
"""

import json
import logging

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import SATURATION_CHECK_PROMPT
from taxonomy_generator.schemas import SaturationCheckOutput
from taxonomy_generator.state import State, UserFeedback
from taxonomy_generator.utils import format_taxonomy, load_chat_model

logger = logging.getLogger(__name__)


def _setup_saturation_chain(configuration: Configuration):
    """Set up the chain for the saturation check."""
    model = load_chat_model(configuration.fast_llm)
    structured_model = model.with_structured_output(SaturationCheckOutput)
    prompt = SATURATION_CHECK_PROMPT.partial(use_case=configuration.use_case)
    return (prompt | structured_model).with_config(run_name="CheckSaturation")


def _codes_for_batch(state: State, batch_idx: int) -> list:
    """Return the open codes belonging to the minibatch at ``batch_idx``."""
    doc_ids = set()
    for idx in state.minibatches[batch_idx]:
        doc = state.documents[idx]
        doc_ids.add(doc["id"] if isinstance(doc, dict) else doc.id)
    return [
        {"label": c.get("label", ""), "rationale": c.get("rationale", "")}
        for c in state.open_codes
        if c.get("doc_id") in doc_ids
    ]


async def check_saturation(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Check saturation of the latest taxonomy against the latest open codes."""
    configuration = Configuration.from_runnable_config(config)

    # The batch just open-coded and axially processed is at index
    # (open_code_batch_index - 1) because open coding advances the index.
    batch_idx = max(state.open_code_batch_index - 1, 0)
    codes = _codes_for_batch(state, batch_idx)
    taxonomy = state.clusters[-1] if state.clusters else []
    taxonomy_json = format_taxonomy(taxonomy)

    logger.info(
        "Checking saturation — minibatch %d/%d, %d codes vs %d dimensions (model: %s)",
        batch_idx + 1, len(state.minibatches), len(codes), len(taxonomy), configuration.fast_llm,
    )

    chain = _setup_saturation_chain(configuration)
    result: SaturationCheckOutput = await chain.ainvoke(
        {
            "taxonomy_json": taxonomy_json,
            "codes_json": json.dumps(codes, indent=2),
        }
    )

    streak = state.saturation_streak + 1 if result.is_saturated else 0

    logger.info(
        "Saturation verdict: %s (streak %d/%d, uncovered: %s)",
        "saturated" if result.is_saturated else "not saturated",
        streak,
        configuration.saturation_streak_threshold,
        result.uncovered_concepts,
    )

    # Automated critic: reuse the existing {feedback} slot so uncovered concepts
    # flow into the next update_taxonomy pass (design principle #3). When there
    # is nothing to report, clear the slot so stale critic feedback does not
    # accumulate across iterations.
    feedback_update = None
    if not result.is_saturated and result.uncovered_concepts:
        uncovered = "; ".join(result.uncovered_concepts)
        feedback_update = UserFeedback(
            decision="modify",
            explanation=(
                "Automated saturation critic: the current minibatch's open codes "
                "reveal concepts the taxonomy does not cover."
            ),
            feedback=(
                f"The following concepts from the latest minibatch are not covered by any "
                f"existing dimension: {uncovered}. Extend or adjust the taxonomy to cover them."
            ),
        )

    return {
        "saturation_history": [{
            "batch_index": batch_idx,
            "is_saturated": result.is_saturated,
            "uncovered_concepts": result.uncovered_concepts,
            "rationale": result.rationale,
        }],
        "saturation_streak": streak,
        "user_feedback": feedback_update,
        "status": [
            f"Saturation check for minibatch {batch_idx + 1}: "
            f"{'saturated' if result.is_saturated else 'not saturated'} (streak {streak})."
        ],
    }