"""Node for selecting dimensions relevant to the use case (selective coding).

Filters the reviewed, value-consolidated taxonomy to the subset of
dimensions that serve the use case. Dropped dimensions are kept
inspectable — recorded with rationales in the status/explanations
accumulators and omitted only from ``selected_clusters`` — never silently
deleted from the full taxonomy.
"""

import logging

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import DIMENSION_SELECTION_PROMPT
from taxonomy_generator.schemas import SelectionOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import format_taxonomy, load_chat_model

logger = logging.getLogger(__name__)


def _setup_selection_chain(configuration: Configuration):
    """Set up the chain for use-case relevance selection."""
    model = load_chat_model(configuration.model)
    structured_model = model.with_structured_output(SelectionOutput)
    prompt = DIMENSION_SELECTION_PROMPT.partial(use_case=configuration.use_case)
    return (prompt | structured_model).with_config(run_name="SelectDimensions")


async def select_dimensions(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Select the dimensions relevant to the use case from the final taxonomy."""
    configuration = Configuration.from_runnable_config(config)

    final = state.clusters[-1] if state.clusters else []
    if not final:
        logger.warning("No taxonomy to select from — skipping selection")
        return {"status": ["Dimension selection skipped (no taxonomy)."]}

    logger.info(
        "Selecting dimensions relevant to the use case from %d candidates (model: %s)",
        len(final), configuration.model,
    )

    chain = _setup_selection_chain(configuration)
    result: SelectionOutput = await chain.ainvoke(
        {"taxonomy_json": format_taxonomy(final)}
    )

    by_id = {str(c.get("id")): c for c in final if isinstance(c, dict)}

    # Preserve the model's relevance ordering for the selected subset.
    selected = [by_id[i] for i in result.selected_ids if i in by_id]
    # Keep dropped dimensions inspectable with their rationales.
    dropped = [d.model_dump() for d in result.dropped]

    unknown_selected = [i for i in result.selected_ids if i not in by_id]
    if unknown_selected:
        logger.warning("Selection returned unknown dimension ids: %s", unknown_selected)

    missing_drop_rationales = [str(c.get("id")) for c in selected if str(c.get("id")) in {d["id"] for d in dropped}]
    if missing_drop_rationales:
        logger.warning(
            "Dimensions both selected and dropped — keeping them selected: %s",
            missing_drop_rationales,
        )
        dropped = [d for d in dropped if d["id"] not in missing_drop_rationales]
        selected = [by_id[i] for i in result.selected_ids if i in by_id]

    logger.info(
        "Dimension selection complete — kept %d of %d, dropped %d",
        len(selected), len(final), len(dropped),
    )

    status = [f"Dimension selection: kept {len(selected)}/{len(final)} dimensions."]
    if dropped:
        drop_summary = "; ".join(f"{d['id']} ({d['rationale']})" for d in dropped)
        status.append(f"Dropped dimensions (kept inspectable): {drop_summary}")

    return {
        "selected_clusters": [selected],
        "explanations": [result.rationale],
        "status": status,
    }