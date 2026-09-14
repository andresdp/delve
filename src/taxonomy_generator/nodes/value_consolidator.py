"""Node for consolidating draft values within each dimension.

Implements the value consolidation algorithm from
``TAXONOMY_QUALITY_PLAN.md`` §6:

1. Embed each draft value's ``label + description`` using the configured
   embedding model.
2. L2-normalize the vectors before any distance computation.
3. Partition each dimension's values by ``status`` (accepted / rejected /
   outcome) before any distance computation — a value only ever competes
   with other values that share its status. An accepted decision and a
   rejected one never merge, no matter how close their embeddings are.
4. Compute pairwise distances **within each status partition of each
   dimension only** — a value only competes with other values on the same
   axis and of the same status.
5. Threshold-merge any pair below ``epsilon`` via union-find connected
   components (deterministic, no LLM cost).
6. Borderline pairs (distance just above ``epsilon``, within the borderline
   band) go to an LLM adjudication call — only ever run within a status
   partition, so cross-status pairs are never sent to the LLM.
7. Canonical label per merged group: the nearest-to-centroid value. The
   consolidated value's ``status`` is copied from the canonical member
   (every member of a group shares one status, by construction of step 3).
   Ids are assigned by a running counter across every status partition of
   a dimension, so numbering does not restart per partition.

Nothing is silently deleted: merged-away values are recorded (id and
label) on the consolidated value's ``merged_from`` field and logged for
inspection. The grounded-theory report surfaces this on the merged
value's catalog entry — see ``report_renderer.render_catalog``.
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
) -> Tuple[Dict, List[str]]:
    """Build one consolidated value from a merge group.

    The canonical label/description is taken from the value nearest to the
    group centroid (deterministic). Supporting doc ids are the union across
    the group; merged-away labels are recorded in the returned provenance
    (empty when the group has a single member — nothing was merged).
    """
    centroid = group_vectors.mean(axis=0)
    # Nearest to centroid among *normalized* vectors: smallest Euclidean distance.
    dists = np.linalg.norm(group_vectors - centroid, axis=1)
    canonical_idx = int(np.argmin(dists))
    canonical = group_values[canonical_idx]

    supporting = []
    merged_from = []
    for i, value in enumerate(group_values):
        supporting.extend(value.get("supporting_doc_ids") or [])
        if i != canonical_idx:
            merged_from.append({
                "id": value.get("id", "?"),
                "label": value.get("label", ""),
            })

    supporting_ids = list(dict.fromkeys(supporting))  # stable dedupe

    consolidated = {
        "id": f"{dimension_id}.{index_offset}",
        "dimension_id": dimension_id,
        "label": canonical.get("label", ""),
        "description": canonical.get("description", ""),
        "supporting_doc_ids": supporting_ids,
        "merged_from": merged_from,
        # Partitioning by status (consolidate_values) guarantees every member
        # of this group shares one status — a direct copy is always correct.
        "status": canonical.get("status", "accepted"),
    }

    merged_labels = [m["label"] or m["id"] for m in merged_from]
    return consolidated, merged_labels


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
                iteration_index=len(state.clusters) + 1,
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
    merge_descriptions: List[str] = []
    kept_as_is_count = 0
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
            kept_as_is_count += len(dim_values)
            continue

        dim_name = cluster.get("name") or dim_id

        # Step 3: partition by status — a value only ever competes with
        # other values that share its status. Dict insertion order gives a
        # deterministic partition order (first-seen status in dim_values).
        status_groups: Dict[str, List[Dict]] = {}
        for v in dim_values:
            status_groups.setdefault(v.get("status", "accepted"), []).append(v)

        # Run the existing pairwise-distance / threshold-merge / borderline
        # LLM-adjudication / canonical-selection sequence independently per
        # status partition, then concatenate before renumbering ids once
        # across the whole dimension (below) — not restarted per partition.
        raw_new_values: List[Dict] = []
        for status_values in status_groups.values():
            group_vector_rows = [global_ids[v["id"]] for v in status_values]
            group_vectors_all = vectors[group_vector_rows]

            # Step 4: pairwise distances within this status partition only.
            dist_matrix = pairwise_euclidean(group_vectors_all)

            # Step 5: threshold merge edges (deterministic union-find).
            merge_edges: List[Tuple[int, int]] = []
            # Step 6: collect borderline pairs for LLM adjudication.
            borderline_pairs: List[Tuple[int, int]] = []
            for i in range(len(status_values)):
                for j in range(i + 1, len(status_values)):
                    d = float(dist_matrix[i, j])
                    if d <= epsilon:
                        merge_edges.append((i, j))
                    elif d <= borderline_upper:
                        borderline_pairs.append((i, j))

            # LLM adjudication for borderline pairs (bounded, sequential for
            # clarity). Only same-status pairs ever reach this point.
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
                                "id": status_values[i]["id"],
                                "label": status_values[i].get("label", ""),
                                "description": status_values[i].get("description", ""),
                                "supporting_doc_ids": status_values[i].get("supporting_doc_ids", []),
                            }, indent=2),
                            "value_b_json": json.dumps({
                                "id": status_values[j]["id"],
                                "label": status_values[j].get("label", ""),
                                "description": status_values[j].get("description", ""),
                                "supporting_doc_ids": status_values[j].get("supporting_doc_ids", []),
                            }, indent=2),
                        }
                    )
                    if verdict.same_decision:
                        merge_edges.append((i, j))
                        logger.info(
                            "Borderline merge approved by LLM within %s: %s + %s (d=%.3f) — %s",
                            dim_id, status_values[i]["id"], status_values[j]["id"],
                            float(dist_matrix[i, j]), verdict.rationale,
                        )
                    else:
                        logger.debug(
                            "Borderline merge rejected by LLM within %s: %s vs %s (d=%.3f)",
                            dim_id, status_values[i]["id"], status_values[j]["id"],
                            float(dist_matrix[i, j]),
                        )
                except Exception as e:
                    logger.warning(
                        "Borderline adjudication failed for %s/%s — keeping values separate: %s",
                        status_values[i]["id"], status_values[j]["id"], e,
                    )

            components = connected_components(len(status_values), merge_edges)

            # Step 7: canonical label per group (nearest-to-centroid).
            # ``len(raw_new_values) + 1`` is a running counter across every
            # status partition of this dimension (it only ever grows, via
            # the append below), so the id assigned here is already the
            # final, dimension-wide sequential id — numbering does not
            # restart per partition, with no separate renumbering pass
            # needed afterward.
            for members in components:
                group_values = [status_values[m] for m in members]
                group_vectors = group_vectors_all[members]
                consolidated, merged_labels = _merge_group(
                    group_values, group_vectors, dim_id, len(raw_new_values) + 1
                )
                raw_new_values.append(consolidated)
                if merged_labels:
                    canonical_label = consolidated["label"] or consolidated["id"]
                    sources = ", ".join(f'"{label}"' for label in merged_labels)
                    merge_descriptions.append(
                        f'[{dim_name}] {sources} → "{canonical_label}"'
                    )
                else:
                    kept_as_is_count += 1

        new_values: List[Dict] = raw_new_values

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
            stage="consolidate", iteration_index=len(state.clusters) + 1,
        )

    summary = (
        f"Consolidated {len(all_values)} draft values across {len(reviewed)} dimensions "
        f"(merge threshold {epsilon:.3f}, borderline band {band:.3f})."
    )
    if merge_descriptions:
        merges_text = "\n".join(f"  - {d}" for d in merge_descriptions)
        explanation = (
            f"{summary} Merged {len(merge_descriptions)} near-duplicate value"
            f"{'s' if len(merge_descriptions) != 1 else ''}:\n{merges_text}"
        )
        if kept_as_is_count:
            explanation += (
                f"\nThe remaining {kept_as_is_count} value"
                f"{'s were' if kept_as_is_count != 1 else ' was'} distinct enough to keep as generated."
            )
    else:
        explanation = f"{summary} No values were merged — all {kept_as_is_count} remained distinct."

    return {
        "clusters": [consolidated_clusters],
        "explanations": [explanation],
        "status": [f"Value consolidation complete: {len(all_values)} draft values processed."],
    }