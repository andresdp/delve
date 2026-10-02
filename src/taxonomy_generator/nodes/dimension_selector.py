"""Node for selecting dimensions relevant to the use case (selective coding).

Filters the reviewed, value-consolidated taxonomy to the subset of
dimensions that serve the use case. Dropped dimensions are kept
inspectable — recorded with rationales in ``dropped_dimensions`` (and
mirrored into the ``status`` log) and omitted only from
``selected_clusters`` — never silently deleted from the full taxonomy.
"""

import logging
from typing import Dict, List, Tuple

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.nodes.evidence_linker import CANDIDATE_STATUSES
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


def split_by_support(clusters: List[Dict], min_sources: int) -> Tuple[List[Dict], List[Dict]]:
    """Separate dimensions whose evidence comes from fewer than ``min_sources`` sources.

    Grounded theory keeps a category only when it recurs across incidents; a
    dimension backed by a single source is usually one document's wording of
    a decision another dimension already covers. Uses the ``evidence`` summary
    written by evidence linking. Returns ``(kept, dropped_records)``; does
    nothing when the rule is off, when any dimension lacks an evidence summary,
    or when it would drop every dimension.
    """
    dims = [c for c in clusters if isinstance(c, dict)]
    if min_sources <= 0 or not dims or not all(isinstance(c.get("evidence"), dict) for c in dims):
        return clusters, []
    weak = [c for c in dims if c["evidence"].get("sources", 0) < min_sources]
    if not weak or len(weak) == len(dims):
        if weak:
            logger.warning("Minimum-support rule would drop every dimension — skipped")
        return clusters, []
    dropped = [{
        "id": str(c.get("id")),
        "rationale": (f"Insufficient evidence: supported by {c['evidence'].get('sources', 0)} source(s) "
                      f"({c['evidence'].get('documents', 0)} document(s)); at least {min_sources} required."),
    } for c in weak]
    weak_ids = {str(c.get("id")) for c in weak}
    return [c for c in clusters if str(c.get("id")) not in weak_ids], dropped




def split_by_candidates(clusters: List[Dict], min_candidates: int) -> Tuple[List[Dict], List[Dict]]:
    """Separate dimensions with fewer than ``min_candidates`` candidate decisions.

    A decision point's values are candidate decisions, i.e. alternative answers
    to one question (status ``accepted``, ``rejected`` or ``mixed``). Values with status
    ``outcome`` are effects of decisions, so a dimension holding only outcomes
    (or a single candidate) is not a decision point. Returns
    ``(kept, dropped_records)``; does nothing when the rule is off or when it
    would drop every dimension.
    """
    dims = [c for c in clusters if isinstance(c, dict)]
    if min_candidates <= 0 or not dims:
        return clusters, []

    def candidates(cluster: Dict) -> int:
        return sum(1 for v in cluster.get("values") or []
                   if isinstance(v, dict) and v.get("status", "accepted") in CANDIDATE_STATUSES)

    weak = [c for c in dims if candidates(c) < min_candidates]
    if not weak or len(weak) == len(dims):
        if weak:
            logger.warning("Candidate-decision rule would drop every dimension — skipped")
        return clusters, []
    dropped = [{
        "id": str(c.get("id")),
        "rationale": (f"Not a decision point: {candidates(c)} candidate decision(s) "
                      f"(accepted/rejected/mixed values) besides outcomes; at least {min_candidates} required."),
    } for c in weak]
    weak_ids = {str(c.get("id")) for c in weak}
    return [c for c in clusters if str(c.get("id")) not in weak_ids], dropped


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

    candidates, support_dropped = split_by_support(final, int(configuration.min_dimension_sources or 0))
    if support_dropped:
        logger.info(
            "Minimum-support rule dropped %d of %d dimensions (fewer than %d sources)",
            len(support_dropped), len(final), configuration.min_dimension_sources,
        )
    candidates, decision_dropped = split_by_candidates(
        candidates, int(configuration.min_candidate_decisions or 0))
    if decision_dropped:
        logger.info(
            "Candidate-decision rule dropped %d dimensions (fewer than %d candidate decisions)",
            len(decision_dropped), configuration.min_candidate_decisions,
        )
    support_dropped = support_dropped + decision_dropped

    logger.info(
        "Selecting dimensions relevant to the use case from %d candidates (model: %s)",
        len(candidates), configuration.model,
    )

    chain = _setup_selection_chain(configuration)
    result: SelectionOutput = await chain.ainvoke(
        {"taxonomy_json": format_taxonomy(candidates)}
    )

    by_id = {str(c.get("id")): c for c in candidates if isinstance(c, dict)}

    # Preserve the model's relevance ordering for the selected subset.
    selected = [by_id[i] for i in result.selected_ids if i in by_id]
    # Keep dropped dimensions inspectable with their rationales.
    dropped = support_dropped + [d.model_dump() for d in result.dropped]

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
        "dropped_dimensions": dropped,
        "explanations": [result.rationale],
        "status": status,
    }