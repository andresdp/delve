"""Consistency comparison across saved taxonomies.

Aligns dimensions from two or more taxonomy views (typically saved runs over
the same corpus) into recurring groups and one-offs, plus an overall
agreement signal — the post-hoc comparison engine for multi-run consistency
assessment.

Alignment follows the two-tier pattern from ``value_consolidator.py``:
embed dimension ``name + description`` (plus value labels when present),
L2-normalize, greedily align below ``evaluation.consistency_threshold``
(deterministic, no LLM cost), and route pairs inside the borderline band to
one judge call for same-dimension adjudication. Embedding loader failure
degrades to exact-name matching with a logged warning.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation.judge import resolve_judge_model
from taxonomy_generator.utils import (
    connected_components,
    l2_normalize,
    load_embeddings_model,
)

logger = logging.getLogger(__name__)


def _dimension_text(cluster: Dict) -> str:
    """Serialize one dimension for embedding: name + description + value labels."""
    parts = [cluster.get("name", ""), cluster.get("description", "")]
    for value in cluster.get("values") or []:
        if isinstance(value, dict) and value.get("label"):
            parts.append(value["label"])
    return " ".join(p for p in parts if p).strip()


def _dimension_label(cluster: Dict, file_index: int, dim_index: int) -> Dict:
    """Build the identifying record for one dimension occurrence."""
    return {
        "file": file_index,
        "index": dim_index,
        "id": cluster.get("id", str(dim_index + 1)),
        "name": cluster.get("name", "Unnamed"),
    }


async def _adjudicate_same_dimension(prompt: str, model: str | None) -> bool:
    """Ask the judge one same-dimension question; any failure rejects."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8,
        temperature=0.0,
    )
    answer = (response.choices[0].message.content or "").strip().upper()
    return answer.startswith("YES")


def _cross_distances(vectors: np.ndarray) -> np.ndarray:
    """Full pairwise Euclidean distance matrix for normalized row vectors."""
    sq = np.sum(vectors ** 2, axis=1)
    sq_dists = sq[:, None] + sq[None, :] - 2.0 * (vectors @ vectors.T)
    np.maximum(sq_dists, 0.0, out=sq_dists)
    return np.sqrt(sq_dists)


async def compare_taxonomies(
    taxonomies: List[List[Dict]], configuration: Configuration
) -> Dict:
    """Compare two or more taxonomy views for run-to-run consistency.

    Args:
        taxonomies: One cluster list per saved taxonomy file.
        configuration: The run configuration (evaluation + embedding settings).

    Returns:
        A comparison dict: ``{"files": N, "agreement": float | None,
        "recurring": [...], "one_offs": [...], "unavailable": False}`` — or
        the unavailable marker on total failure.
    """
    threshold = configuration.evaluation_consistency_threshold
    band = configuration.evaluation_consistency_borderline_band

    # Flatten all dimensions with (file, index) identity.
    dims: List[Dict] = []
    texts: List[str] = []
    for file_index, clusters in enumerate(taxonomies):
        for dim_index, cluster in enumerate(clusters or []):
            if isinstance(cluster, dict):
                dims.append(_dimension_label(cluster, file_index, dim_index))
                texts.append(_dimension_text(cluster))

    max_count = max((len(c or []) for c in taxonomies), default=0)

    try:
        fallback: str | None = None
        distances = None
        try:
            if texts:
                embeddings = np.asarray(
                    load_embeddings_model(configuration.embedding).embed_documents(texts),
                    dtype=float,
                )
                vectors = l2_normalize(embeddings)
                if len(texts) > 1:
                    distances = _cross_distances(vectors)
        except Exception as embed_exc:  # noqa: BLE001 — degrade, don't fail
            logger.warning(
                "Consistency embedding unavailable (%s) — falling back to exact-name matching",
                embed_exc,
            )
            fallback = "exact-name"

        edges: List[Tuple[int, int]] = []
        adjudicated = 0
        if distances is not None:
            judge_model = resolve_judge_model(
                configuration.evaluation_judge_model or configuration.model
            )
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    # Recurring means across files; skip same-file pairs.
                    if dims[i]["file"] == dims[j]["file"]:
                        continue
                    d = float(distances[i, j])
                    if d <= threshold:
                        edges.append((i, j))
                    elif d <= threshold + band:
                        prompt = (
                            "Two taxonomy dimensions from runs over the same corpus:\n"
                            f"A: {texts[i]}\nB: {texts[j]}\n\n"
                            "Do A and B capture the same underlying axis of "
                            "variation? Answer YES or NO only."
                        )
                        try:
                            if await _adjudicate_same_dimension(prompt, judge_model):
                                edges.append((i, j))
                                adjudicated += 1
                        except Exception as judge_exc:  # noqa: BLE001
                            logger.warning(
                                "Borderline adjudication failed for pair (%d, %d): %s — rejecting",
                                i, j, judge_exc,
                            )
        elif fallback == "exact-name":
            by_name: Dict[str, List[int]] = {}
            for idx, dim in enumerate(dims):
                by_name.setdefault(dim["name"].strip().lower(), []).append(idx)
            for indices in by_name.values():
                files = {dims[i]["file"] for i in indices}
                if len(files) > 1:
                    edges.extend((indices[0], other) for other in indices[1:])

        groups = connected_components(len(texts), edges)

        recurring: List[Dict] = []
        one_offs: List[Dict] = []
        aligned = 0
        for group in groups:
            files_in_group = {dims[i]["file"] for i in group}
            if len(files_in_group) > 1:
                recurring.append(
                    {
                        "dimensions": [dims[i] for i in group],
                        "files": sorted(files_in_group),
                    }
                )
                aligned += len(files_in_group)
            else:
                one_offs.append(dims[group[0]])

        agreement = round(aligned / max_count, 4) if max_count else None
        return {
            "files": len(taxonomies),
            "agreement": agreement,
            "recurring": recurring,
            "one_offs": one_offs,
            "adjudicated_pairs": adjudicated,
            "fallback": fallback,
            "unavailable": False,
        }
    except Exception as exc:  # noqa: BLE001 — degrade, don't fail (R7)
        logger.warning("Consistency comparison unavailable: %s", exc)
        return {"unavailable": True, "error": str(exc)}