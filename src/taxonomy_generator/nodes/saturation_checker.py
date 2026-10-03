"""Node for checking theoretical saturation of the taxonomy.

Runs after each ``generate_taxonomy``/``update_taxonomy`` pass. Saturation
asks whether *new* data still brings new concepts, so the latest minibatch's
open codes are compared against the taxonomy as it was **before** that
minibatch was incorporated (``clusters[-2]``), not against the taxonomy just
updated with them (which would cover them by construction). The minibatch a
taxonomy was generated from (no earlier taxonomy) is never counted as
saturated. Uncovered concepts feed back into the existing feedback mechanism
as an automated critic.
"""

import json
import logging

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import SATURATION_CHECK_PROMPT
from taxonomy_generator.schemas import SaturationCheckOutput
from taxonomy_generator.state import State, UserFeedback
from taxonomy_generator.utils import format_taxonomy, load_chat_model, taxonomy_prompt_view

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


def saturation_coverage(n_codes: int, n_uncovered: int) -> float:
    """Share of a minibatch's open codes the taxonomy already covers (1.0 when there are no codes)."""
    if n_codes <= 0:
        return 1.0
    return 1.0 - min(n_uncovered, n_codes) / n_codes


async def check_saturation(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Check whether the latest minibatch's open codes were new to the taxonomy."""
    configuration = Configuration.from_runnable_config(config)

    # The batch just open-coded and axially processed is at index
    # (open_code_batch_index - 1) because open coding advances the index.
    batch_idx = max(state.open_code_batch_index - 1, 0)
    codes = _codes_for_batch(state, batch_idx)

    # Test against the taxonomy before this batch was incorporated. Without one
    # (the batch the taxonomy was generated from), there is nothing to test.
    if len(state.clusters) < 2:
        logger.info(
            "Saturation not tested for minibatch %d/%d — the taxonomy was generated from it",
            batch_idx + 1, len(state.minibatches),
        )
        return {
            "saturation_history": [{
                "batch_index": batch_idx,
                "is_saturated": False,
                "checker_is_saturated": None,
                "coverage": None,
                "codes": len(codes),
                "streak": 0,
                "uncovered_concepts": [],
                "rationale": "Not tested: the taxonomy was generated from this minibatch.",
            }],
            "saturation_streak": 0,
            "user_feedback": None,
            "status": [f"Saturation not tested for minibatch {batch_idx + 1} (generation batch)."],
        }

    taxonomy = state.clusters[-2]
    taxonomy_json = format_taxonomy(taxonomy_prompt_view(taxonomy))

    logger.info(
        "Checking saturation — minibatch %d/%d, %d codes vs %d dimensions before this batch (model: %s)",
        batch_idx + 1, len(state.minibatches), len(codes), len(taxonomy), configuration.fast_llm,
    )

    chain = _setup_saturation_chain(configuration)
    result: SaturationCheckOutput = await chain.ainvoke(
        {
            "taxonomy_json": taxonomy_json,
            "codes_json": json.dumps(codes, indent=2),
        }
    )

    coverage = saturation_coverage(len(codes), len(result.uncovered_concepts))
    min_coverage = float(configuration.saturation_min_coverage if configuration.saturation_min_coverage is not None else 1.0)
    # Saturated when the checker says so, or (tolerant mode, min_coverage < 1)
    # when enough of the minibatch's codes are already covered: with detailed
    # passages almost every minibatch has *something* new, so the strict rule
    # never stops and the taxonomy keeps growing.
    saturated = result.is_saturated or (min_coverage < 1.0 and coverage >= min_coverage)
    streak = state.saturation_streak + 1 if saturated else 0

    logger.info(
        "Saturation verdict: %s (coverage %.2f, min %.2f, streak %d/%d, uncovered: %s)",
        "saturated" if saturated else "not saturated",
        coverage, min_coverage,
        streak,
        configuration.saturation_streak_threshold,
        result.uncovered_concepts,
    )

    # Automated critic: reuse the existing {feedback} slot so uncovered concepts
    # flow into the next update_taxonomy pass (design principle #3). When there
    # is nothing to report, clear the slot so stale critic feedback does not
    # accumulate across iterations.
    feedback_update = None
    if not saturated and result.uncovered_concepts:
        uncovered = "; ".join(result.uncovered_concepts)
        feedback_update = UserFeedback(
            decision="modify",
            explanation=(
                "Automated saturation critic: the latest minibatch's open codes "
                "revealed concepts the taxonomy did not cover before that minibatch."
            ),
            feedback=(
                f"The following concepts from the latest minibatch were not covered by any "
                f"dimension before it was incorporated: {uncovered}. Check that the taxonomy "
                f"now covers them, preferring to add them as values of an existing dimension "
                f"when they are options for a decision it already names; add a new dimension "
                f"only for a genuinely different design decision."
            ),
        )

    return {
        "saturation_history": [{
            "batch_index": batch_idx,
            "is_saturated": saturated,
            "checker_is_saturated": result.is_saturated,
            "coverage": round(coverage, 3),
            "codes": len(codes),
            "streak": streak,
            "uncovered_concepts": result.uncovered_concepts,
            "rationale": result.rationale,
        }],
        "saturation_streak": streak,
        "user_feedback": feedback_update,
        "status": [
            f"Saturation check for minibatch {batch_idx + 1}: "
            f"{'saturated' if saturated else 'not saturated'} "
            f"(coverage {coverage:.0%}, streak {streak})."
        ],
    }