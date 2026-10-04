"""Merge near-duplicate dimensions (same design decision under different names).

Axial coding rewrites the taxonomy every minibatch and tends to add a new
dimension for each new wording of an existing decision. Value consolidation
only merges values *within* a dimension, so these duplicates survive to the
end (34 and 43 dimensions in the first two benchmark runs).

This step runs before value consolidation:

1. Embed each dimension as ``<name>. <description> Options: <value labels>``.
2. Pairs within ``dimension_merge_distance_threshold`` (Euclidean distance on
   L2-normalized vectors) merge automatically.
3. Pairs within the following ``dimension_merge_borderline_band`` go to an LLM
   judge (closest first, at most ``MAX_JUDGED_PAIRS``), which merges only when
   both name the same design decision. Related but separate decisions (e.g.
   detecting vs. mitigating a problem) stay separate.
4. Each connected group becomes one dimension: the member with the most values
   gives the name, description and id. Every member's values are kept (value
   consolidation then merges duplicates), ``merged_from`` records the merged
   dimensions, and relations pointing at merged ids are redirected.

Fail-soft: if embedding fails, the taxonomy is returned unchanged.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Tuple

import numpy as np

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import DIMENSION_MERGE_PROMPT
from taxonomy_generator.schemas import DimensionMergeOutput
from taxonomy_generator.utils import (
    connected_components,
    l2_normalize,
    load_chat_model,
    load_embeddings_model,
    pairwise_euclidean,
)

logger = logging.getLogger(__name__)

# Upper bound on LLM judge calls per run (closest pairs are judged first).
MAX_JUDGED_PAIRS = 200


def _dimension_text(cluster: Dict) -> str:
    labels = [v.get("label", "") for v in cluster.get("values") or [] if isinstance(v, dict)]
    text = f"{cluster.get('name', '')}. {cluster.get('description', '')}"
    return (text + (" Options: " + "; ".join(labels[:15]) if labels else "")).strip()


def _judge_payload(cluster: Dict) -> str:
    return json.dumps({
        "name": cluster.get("name", ""),
        "description": cluster.get("description", ""),
        "options": [v.get("label", "") for v in cluster.get("values") or [] if isinstance(v, dict)],
    }, indent=2)


def merge_groups(dims: List[Dict], groups: List[List[int]]) -> Tuple[List[Dict], List[str]]:
    """Combine each group of dimension indices into one dimension (pure, deterministic)."""
    remap: Dict[str, str] = {}
    merged_at: Dict[int, Dict] = {}
    notes: List[str] = []
    for members in groups:
        canonical_idx = max(members, key=lambda i: (len(dims[i].get("values") or []), -i))
        canonical = dict(dims[canonical_idx])
        canonical_id = str(canonical.get("id"))
        if len(members) > 1:
            others = [i for i in members if i != canonical_idx]
            canonical["values"] = [dict(v) for i in [canonical_idx] + others for v in dims[i].get("values") or []]
            canonical["relations"] = [dict(r) for i in [canonical_idx] + others for r in dims[i].get("relations") or []]
            canonical["merged_from"] = list(canonical.get("merged_from") or []) + [
                {"id": str(dims[i].get("id")), "name": dims[i].get("name", "")} for i in others
            ]
            for i in others:
                remap[str(dims[i].get("id"))] = canonical_id
            notes.append(" + ".join(f'"{dims[i].get("name", "")}"' for i in [canonical_idx] + others)
                         + f' → "{canonical.get("name", "")}"')
        merged_at[min(members)] = canonical

    merged = [merged_at[i] for i in sorted(merged_at)]
    for cluster in merged:
        own, seen, relations = str(cluster.get("id")), set(), []
        for rel in cluster.get("relations") or []:
            target = remap.get(str(rel.get("target_id")), str(rel.get("target_id")))
            key = (target, rel.get("type"))
            if target == own or key in seen:
                continue
            seen.add(key)
            relations.append({**rel, "target_id": target})
        cluster["relations"] = relations
    return merged, notes


async def merge_dimensions(clusters: List[Dict], configuration: Configuration) -> Tuple[List[Dict], List[str]]:
    """Merge dimensions that name the same design decision. Returns ``(clusters, notes)``."""
    dims = [c for c in clusters or [] if isinstance(c, dict)]
    if len(dims) < 2:
        return clusters, []

    threshold = float(configuration.dimension_merge_distance_threshold)
    upper = threshold + float(configuration.dimension_merge_borderline_band)
    try:
        embeddings = load_embeddings_model(configuration.embedding)
        vectors = l2_normalize(np.asarray(
            await embeddings.aembed_documents([_dimension_text(c) for c in dims]), dtype=float))
    except Exception as exc:  # noqa: BLE001 — degrade, don't fail the run
        logger.warning("Dimension merging skipped (embedding failed): %s", exc)
        return clusters, []

    dist = pairwise_euclidean(vectors)
    edges: List[Tuple[int, int]] = []
    borderline: List[Tuple[float, int, int]] = []
    for i in range(len(dims)):
        for j in range(i + 1, len(dims)):
            d = float(dist[i, j])
            if d <= threshold:
                edges.append((i, j))
            elif d <= upper:
                borderline.append((d, i, j))
    borderline.sort()
    if len(borderline) > MAX_JUDGED_PAIRS:
        logger.info("Judging the %d closest of %d borderline dimension pairs", MAX_JUDGED_PAIRS, len(borderline))
        borderline = borderline[:MAX_JUDGED_PAIRS]

    if borderline:
        model = load_chat_model(configuration.generation_llm).with_structured_output(DimensionMergeOutput)
        chain = (DIMENSION_MERGE_PROMPT.partial(use_case=configuration.use_case) | model).with_config(
            run_name="AdjudicateDimensionMerge")
        semaphore = asyncio.Semaphore(configuration.summary_max_concurrency or 5)

        async def judge(i: int, j: int):
            async with semaphore:
                try:
                    return await chain.ainvoke({"dimension_a_json": _judge_payload(dims[i]),
                                                "dimension_b_json": _judge_payload(dims[j])})
                except Exception as exc:  # noqa: BLE001 — a failed judgment keeps them separate
                    logger.warning("Dimension-merge judgment failed for %s/%s: %s",
                                   dims[i].get("id"), dims[j].get("id"), exc)
                    return None

        verdicts = await asyncio.gather(*(judge(i, j) for _, i, j in borderline))
        for (d, i, j), verdict in zip(borderline, verdicts):
            if verdict is not None and verdict.same_decision:
                edges.append((i, j))
                logger.info("Dimension merge approved (d=%.3f): %s + %s — %s",
                            d, dims[i].get("name"), dims[j].get("name"), verdict.rationale)

    groups = connected_components(len(dims), edges)
    merged, notes = merge_groups(dims, groups)
    if notes:
        logger.info("Merged %d dimensions into %d", len(dims), len(merged))
    return merged, notes
