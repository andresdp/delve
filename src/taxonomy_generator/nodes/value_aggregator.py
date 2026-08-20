"""Node for aggregating proposed new values in test mode.

Runs after ``label_documents`` in test mode only. The seeded taxonomy's
dimensions are frozen (per the reusable-taxonomies contract), but documents
whose specific decision fits no existing value of their dimension may have
proposed a new value label during labeling. This node deduplicates those
proposals and appends the survivors to their dimensions:

1. Collect documents with a real (non-fallback) category and a value label
   that does not case-insensitively match an existing label of that dimension.
2. Surviving proposals are deduplicated among themselves by embedding
   distance (``value_merge_distance_threshold``) so repeated new decisions
   collapse into one value.
3. Appended values record the contributing documents as supporting evidence
   and continue the dimension's existing value-id scheme.

When embedding fails (provider error, missing key), the node degrades to
exact-string dedup only — a test run must never fail because of dedup.

Emits the updated clusters as a new iteration (seed -> value-extended seed)
plus a ``delta_summary`` (new values per dimension; fallback documents).
"""

import copy
import logging
import re
from typing import Dict, List, Tuple

import numpy as np
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State
from taxonomy_generator.utils import l2_normalize, load_embeddings_model, pairwise_euclidean

logger = logging.getLogger(__name__)


def _norm_label(label: str) -> str:
    """Normalize a value label for exact-string comparison."""
    return re.sub(r"\s+", " ", (label or "").strip().lower())


def _existing_value_labels(cluster: Dict) -> List[str]:
    return [
        (v.get("label") or "")
        for v in (cluster.get("values") or [])
        if isinstance(v, dict)
    ]


def _collect_candidates(
    documents: List, clusters: List[Dict], fallback_category: str
) -> Dict[str, List[Dict]]:
    """Group new-value proposals by dimension id.

    A document is a candidate when it has a real category matching a frozen
    dimension and a value that does not match that dimension's existing labels.
    """
    by_name = {c.get("name"): c for c in clusters if isinstance(c, dict)}
    candidates: Dict[str, List[Dict]] = {}
    for doc in documents:
        category = doc["category"] if isinstance(doc, dict) else doc.category
        value = doc["value"] if isinstance(doc, dict) else doc.value
        doc_id = doc["id"] if isinstance(doc, dict) else doc.id
        if not category or not value or category == fallback_category:
            continue
        cluster = by_name.get(category)
        if cluster is None:
            # Unknown category name (e.g. a fallback variant) — never a candidate.
            continue
        if _norm_label(value) in {_norm_label(v) for v in _existing_value_labels(cluster)}:
            continue
        candidates.setdefault(cluster.get("id"), []).append({
            "doc_id": doc_id,
            "label": value,
            "dimension_id": cluster.get("id"),
            "dimension_name": cluster.get("name"),
        })
    return candidates


def _next_value_id(cluster: Dict) -> str:
    """Return the next value id continuing the dimension's existing scheme."""
    existing = cluster.get("values") or []
    max_sub = 0
    for v in existing:
        if isinstance(v, dict):
            m = re.match(r"^(?:[^.]+\.)?(\d+)$", str(v.get("id", "")))
            if m:
                max_sub = max(max_sub, int(m.group(1)))
    return f"{cluster.get('id', '0')}.{max_sub + 1}"


async def _dedup_proposals(
    proposals: List[Dict], existing_labels: List[str], configuration: Configuration
) -> Tuple[List[Dict], int]:
    """Deduplicate proposals against existing values and each other.

    Returns ``(survivors, collapsed_count)`` — survivors are proposals that
    represent genuinely new decisions; collapsed_count counts proposals that
    matched an existing value or collapsed into an earlier surviving proposal.
    """
    # Exact-string pass first (free, always available).
    survivors: List[Dict] = []
    collapsed = 0
    seen = {_norm_label(l) for l in existing_labels}
    for p in proposals:
        key = _norm_label(p["label"])
        if key in seen:
            collapsed += 1
            continue
        survivors.append(p)
        seen.add(key)

    if len(survivors) <= 1:
        return survivors, collapsed

    # Embedding pass: drop near-duplicates among survivors.
    try:
        embeddings = load_embeddings_model(configuration.embedding)
        texts = [p["label"] for p in survivors]
        raw_vectors = np.asarray(await embeddings.aembed_documents(texts), dtype=float)
        vectors = l2_normalize(raw_vectors)
        dist = pairwise_euclidean(vectors)
        threshold = configuration.value_merge_distance_threshold

        keep: List[Dict] = []
        kept_indices: List[int] = []
        for i, p in enumerate(survivors):
            if any(dist[i][j] < threshold for j in kept_indices):
                # Collapse into the earliest surviving near-duplicate.
                collapsed += 1
            else:
                keep.append(p)
                kept_indices.append(i)
        return keep, collapsed
    except Exception as e:  # noqa: BLE001 — dedup must never fail the run
        logger.warning(
            "Embedding dedup unavailable for new-value proposals (%s). "
            "Falling back to exact-string dedup only.",
            e,
        )
        return survivors, collapsed


def _fallback_documents(documents: List, fallback_category: str) -> List[Dict]:
    """List documents that landed in the fallback bucket."""
    entries = []
    for doc in documents:
        category = doc["category"] if isinstance(doc, dict) else doc.category
        if category != fallback_category:
            continue
        doc_id = doc["id"] if isinstance(doc, dict) else doc.id
        content = doc["content"] if isinstance(doc, dict) else doc.content
        entries.append({"id": doc_id, "preview": (content or "")[:100]})
    return entries


async def aggregate_new_values(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Append deduplicated new values to the frozen dimensions (test mode)."""
    configuration = Configuration.from_runnable_config(config)

    if not state.clusters:
        logger.error("No clusters in state for value aggregation")
        raise ValueError("No clusters found in state")

    frozen = state.clusters[-1]
    if not state.documents:
        raise ValueError("No labeled documents found in state")

    candidates = _collect_candidates(state.documents, frozen, configuration.fallback_category)

    updated = copy.deepcopy(frozen)
    new_values: List[Dict] = []
    total_collapsed = 0

    for cluster in updated:
        dim_id = cluster.get("id")
        proposals = candidates.get(dim_id, [])
        if not proposals:
            continue
        survivors, collapsed = await _dedup_proposals(
            proposals, _existing_value_labels(cluster), configuration
        )
        total_collapsed += collapsed
        for p in survivors:
            new_value = {
                "id": _next_value_id(cluster),
                "dimension_id": dim_id,
                "label": p["label"],
                "description": f"New value discovered in test mode (from document {p['doc_id']}).",
                "supporting_doc_ids": [p["doc_id"]],
            }
            # Consume the id so consecutive appends within this loop stay unique.
            cluster.setdefault("values", []).append(new_value)
            new_values.append({
                "dimension": cluster.get("name"),
                "dimension_id": dim_id,
                "value": p["label"],
                "value_id": new_value["id"],
                "supporting_doc_ids": [p["doc_id"]],
            })

    delta_summary = {
        "new_values": new_values,
        "fallback_documents": _fallback_documents(state.documents, configuration.fallback_category),
    }

    logger.info(
        "Aggregated new values: %d appended across %d dimensions (%d proposals collapsed)",
        len(new_values), len({nv["dimension_id"] for nv in new_values}), total_collapsed,
    )

    return {
        "clusters": [updated],
        "explanations": [
            f"Test-mode value aggregation: appended {len(new_values)} new values "
            f"({total_collapsed} proposals collapsed as duplicates)."
        ],
        "delta_summary": delta_summary,
        "status": [f"Aggregated {len(new_values)} new values in test mode."],
    }