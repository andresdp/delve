"""Node for consolidating draft values within each dimension.

Implements the value consolidation algorithm from
``TAXONOMY_QUALITY_PLAN.md`` §6:

1. Embed each draft value's ``label + description`` using the configured
   embedding model.
2. L2-normalize the vectors before any distance computation.
3. Compute pairwise distances **within each dimension only** — a value only
   competes with other values on the same axis.
4. Threshold-merge any pair below ``epsilon`` via union-find connected
   components (deterministic, no LLM cost).
5. Borderline pairs (distance just above ``epsilon``, within the borderline
   band) go to an LLM adjudication call.
6. Canonical label per merged group: the nearest-to-centroid value.

Nothing is silently deleted: merged-away values are recorded in the
consolidated value's description metadata and logged for inspection.
"""

import json
import logging
from typing import Dict, List, Tuple

import numpy as np
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import VALUE_MERGE_PROMPT
from taxonomy_generator.schemas import ValueMergeOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import (
    connected_components,
    l2_normalize,
    load_chat_model,
    load_embeddings_model,
    pairwise_euclidean,
)
from taxonomy_generator.visualization import render_taxonomy_biplot, should_render

logger = logging.getLogger(__name__)


def _setup_merge_chain(configuration: Configuration):
    """Set up the chain for borderline value-merge adjudication."""
    model = load_chat_model(configuration.model)
    structured_model = model.with_structured_output(ValueMergeOutput)
    prompt = VALUE_MERGE_PROMPT.partial(use_case=configuration.use_case)
    return (prompt | structured_model).with_config(run_name="AdjudicateValueMerge")


def _flatten_values(clusters: List[Dict]) -> List[Dict]:
    """Flatten all draft values across dimensions, keeping their dimension."""
    values = []
    for cluster in clusters or []:
        if not isinstance(cluster, dict):
            continue
        for value in cluster.get("values") or []:
            if isinstance(value, dict) and value.get("id"):
                values.append(value)
    return values


def _merge_group(
    group_values: List[Dict],
    group_vectors: "np.ndarray",
    dimension_id: str,
    index_offset: int,
) -> Tuple[Dict, str]:
    """Build one consolidated value from a merge group.

    The canonical label/description is taken from the value nearest to the
    group centroid (deterministic). Supporting doc ids are the union across
    the group; merged-away ids are recorded in the returned provenance.
    """
    centroid = group_vectors.mean(axis=0)
    # Nearest to centroid among *normalized* vectors: smallest Euclidean distance.
    dists = np.linalg.norm(group_vectors - centroid, axis=1)
    canonical_idx = int(np.argmin(dists))
    canonical = group_values[canonical_idx]

    supporting = []
    merged_ids = []
    for i, value in enumerate(group_values):
        supporting.extend(value.get("supporting_doc_ids") or [])
        if i != canonical_idx:
            merged_ids.append(value.get("id", "?"))

    supporting_ids = list(dict.fromkeys(supporting))  # stable dedupe

    consolidated = {
        "id": f"{dimension_id}.{index_offset}",
        "dimension_id": dimension_id,
        "label": canonical.get("label", ""),
        "description": canonical.get("description", ""),
        "supporting_doc_ids": supporting_ids,
        "merged_from": merged_ids,
    }

    provenance = (
        f"merged {canonical.get('id')} + {', '.join(merged_ids)}" if merged_ids
        else f"kept {canonical.get('id')} as-is"
    )
    return consolidated, provenance


async def consolidate_values(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Consolidate draft values within each dimension of the reviewed taxonomy."""
    configuration = Configuration.from_runnable_config(config)

    # Optional disable: pass the reviewed taxonomy through untouched (no
    # embeddings, no LLM adjudication). Visualization then places every value
    # at a unitary distance on its dimension axis.
    if not configuration.consolidate_values:
        logger.info("Value consolidation disabled — passing taxonomy through unchanged")
        reviewed = state.clusters[-1] if state.clusters else []
        if should_render(configuration, "consolidate"):
            await render_taxonomy_biplot(
                configuration, reviewed, stage="consolidate",
                iteration_index=len(state.clusters),
            )
        return {
            "clusters": [reviewed],
            "explanations": [
                "Value consolidation disabled (taxonomy.consolidate_values=false); "
                "values kept exactly as generated."
            ],
            "status": ["Value consolidation skipped (disabled)."],
        }

    reviewed = state.clusters[-1] if state.clusters else []
    all_values = _flatten_values(reviewed)

    if not all_values:
        logger.info("No draft values to consolidate — passing taxonomy through")
        return {
            "clusters": [reviewed],
            "explanations": ["No values to consolidate; taxonomy passed through unchanged."],
            "status": ["Value consolidation skipped (no draft values)."],
        }

    logger.info(
        "Consolidating %d draft values across %d dimensions (embedding: %s, epsilon: %.3f, band: %.3f)",
        len(all_values), len(reviewed), configuration.embedding,
        configuration.value_merge_distance_threshold,
        configuration.value_merge_borderline_band,
    )

    embeddings = load_embeddings_model(configuration.embedding)
    texts = [f"{v.get('label', '')}. {v.get('description', '')}".strip() for v in all_values]
    raw_vectors = np.asarray(await embeddings.aembed_documents(texts), dtype=float)
    vectors = l2_normalize(raw_vectors)

    epsilon = float(configuration.value_merge_distance_threshold)
    band = float(configuration.value_merge_borderline_band)
    borderline_upper = epsilon + band

    merge_chain = _setup_merge_chain(configuration)
    merged_provenance: List[str] = []
    # Global row of each draft value in the embedding matrix.
    global_ids = {v["id"]: i for i, v in enumerate(all_values)}

    # Process each dimension independently — values never compete across axes.
    consolidated_clusters: List[Dict] = []
    for cluster in reviewed:
        if not isinstance(cluster, dict):
            consolidated_clusters.append(cluster)
            continue

        dim_id = str(cluster.get("id", "?"))
        dim_values = [v for v in cluster.get("values") or [] if isinstance(v, dict) and v.get("id")]
        new_cluster = dict(cluster)

        if len(dim_values) <= 1:
            # Nothing to merge — keep values but renumber consistently.
            renumbered = [
                {**v, "id": f"{dim_id}.{i + 1}"} for i, v in enumerate(dim_values)
            ]
            new_cluster["values"] = renumbered
            consolidated_clusters.append(new_cluster)
            continue

        dim_vector_rows = [global_ids[v["id"]] for v in dim_values]
        dim_vectors = vectors[dim_vector_rows]

        # Step 3: pairwise distances within this dimension only.
        dist_matrix = pairwise_euclidean(dim_vectors)

        # Step 4: threshold merge edges (deterministic union-find).
        merge_edges: List[Tuple[int, int]] = []
        # Step 5: collect borderline pairs for LLM adjudication.
        borderline_pairs: List[Tuple[int, int]] = []
        for i in range(len(dim_values)):
            for j in range(i + 1, len(dim_values)):
                d = float(dist_matrix[i, j])
                if d <= epsilon:
                    merge_edges.append((i, j))
                elif d <= borderline_upper:
                    borderline_pairs.append((i, j))

        # LLM adjudication for borderline pairs (bounded, sequential for clarity).
        for i, j in borderline_pairs:
            try:
                verdict: ValueMergeOutput = await merge_chain.ainvoke(
                    {
                        "dimension_json": json.dumps({
                            "id": dim_id,
                            "name": cluster.get("name", ""),
                            "description": cluster.get("description", ""),
                        }, indent=2),
                        "value_a_json": json.dumps({
                            "id": dim_values[i]["id"],
                            "label": dim_values[i].get("label", ""),
                            "description": dim_values[i].get("description", ""),
                            "supporting_doc_ids": dim_values[i].get("supporting_doc_ids", []),
                        }, indent=2),
                        "value_b_json": json.dumps({
                            "id": dim_values[j]["id"],
                            "label": dim_values[j].get("label", ""),
                            "description": dim_values[j].get("description", ""),
                            "supporting_doc_ids": dim_values[j].get("supporting_doc_ids", []),
                        }, indent=2),
                    }
                )
                if verdict.same_decision:
                    merge_edges.append((i, j))
                    logger.info(
                        "Borderline merge approved by LLM within %s: %s + %s (d=%.3f) — %s",
                        dim_id, dim_values[i]["id"], dim_values[j]["id"],
                        float(dist_matrix[i, j]), verdict.rationale,
                    )
                else:
                    logger.debug(
                        "Borderline merge rejected by LLM within %s: %s vs %s (d=%.3f)",
                        dim_id, dim_values[i]["id"], dim_values[j]["id"],
                        float(dist_matrix[i, j]),
                    )
            except Exception as e:
                logger.warning(
                    "Borderline adjudication failed for %s/%s — keeping values separate: %s",
                    dim_values[i]["id"], dim_values[j]["id"], e,
                )

        components = connected_components(len(dim_values), merge_edges)

        # Step 6: canonical label per group (nearest-to-centroid).
        new_values: List[Dict] = []
        for offset, members in enumerate(components, start=1):
            group_values = [dim_values[m] for m in members]
            group_vectors = dim_vectors[members]
            consolidated, provenance = _merge_group(
                group_values, group_vectors, dim_id, offset
            )
            new_values.append(consolidated)
            merged_provenance.append(f"[{dim_id}] {provenance}")

        new_cluster["values"] = new_values
        consolidated_clusters.append(new_cluster)

        if len(new_values) < len(dim_values):
            logger.info(
                "Dimension %s: %d draft values consolidated into %d",
                dim_id, len(dim_values), len(new_values),
            )

    # Final biplot of the consolidated values (the "after" picture).
    # The projection is only a view; merge decisions used full distances.
    if should_render(configuration, "consolidate"):
        await render_taxonomy_biplot(
            configuration, consolidated_clusters,
            stage="consolidate", iteration_index=len(state.clusters),
        )

    explanation = (
        f"Consolidated {len(all_values)} draft values. Merge decisions "
        f"(threshold {epsilon:.3f}, borderline band {band:.3f}): "
        + "; ".join(merged_provenance)
    )

    return {
        "clusters": [consolidated_clusters],
        "explanations": [explanation],
        "status": [f"Value consolidation complete: {len(all_values)} draft values processed."],
    }