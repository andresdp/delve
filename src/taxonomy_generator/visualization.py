"""Taxonomy PCA visualization utility (erdogant/pca based).

Renders 2D/3D scatter charts of taxonomy *values* (points) colored by
*dimension* — a debugging/explanation view of value consolidation.

Important caveats built in (TAXONOMY_QUALITY_PLAN.md §7):

- **Merge decisions are never made from projected coordinates.** Only the
  full-dimensional distance computed during consolidation decides merges.
  PCA is a lossy linear projection; two points can look close in projection
  while being far apart in the full embedding space, or vice versa.
- Every chart reports the **explained variance ratio** next to it. When 2–3
  components capture a low share of total variance, the plot is a weak proxy
  for true distance and is labeled as such.

This is a shared utility, not a graph node, because an "iteration" spans
multiple node types. It is called (optionally) from ``generate_taxonomy``,
``update_taxonomy``, ``review_taxonomy``, and ``consolidate_values`` behind
the ``visualization.enabled`` config flag, so it is off by default and adds
no latency/cost to normal runs.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)


async def embed_and_render(
    configuration: Configuration,
    clusters: List[Dict],
    stage: str,
    iteration_index: int,
) -> Optional[Path]:
    """Embed a taxonomy iteration's values and render its PCA chart.

    Convenience wrapper for the axial-coding nodes (generate/update/review):
    embeds each value's ``label + description``, then renders the chart.
    Returns immediately (no embedding cost) when visualization is disabled
    for the stage.
    """
    if not should_render(configuration, stage):
        return None

    points = _collect_value_points(clusters)
    if len(points) < 3:
        return None

    from taxonomy_generator.utils import load_embeddings_model

    embeddings = load_embeddings_model(configuration.embedding)
    texts = [f"{p.get('label', '')}".strip() for p in points]
    raw = np.asarray(await embeddings.aembed_documents(texts), dtype=float)
    vectors_by_value = {p["value_id"]: raw[i] for i, p in enumerate(points)}

    return await render_taxonomy_pca(
        configuration, clusters, vectors_by_value,
        stage=stage, iteration_index=iteration_index,
    )


def _sanitize_name(name: str) -> str:
    """Sanitize a taxonomy name for use in a filename."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", name or "taxonomy").strip("_")
    return cleaned or "taxonomy"


def _collect_value_points(clusters: List[Dict]) -> List[Dict]:
    """Flatten (dimension, value) pairs from a taxonomy iteration."""
    points = []
    for cluster in clusters or []:
        if not isinstance(cluster, dict):
            continue
        dim_id = str(cluster.get("id", "?"))
        dim_name = cluster.get("name", "Unnamed")
        for value in cluster.get("values") or []:
            if isinstance(value, dict):
                points.append({
                    "dimension_id": dim_id,
                    "dimension_name": dim_name,
                    "value_id": value.get("id", "?"),
                    "label": value.get("label", ""),
                })
    return points


def resolve_output_dir(configuration: Configuration) -> Path:
    """Resolve the chart output directory (visualization > --output > default)."""
    out = (
        configuration.visualization_output_dir
        or configuration.default_output_dir
        or "output"
    )
    return Path(out)


def should_render(configuration: Configuration, stage: str) -> bool:
    """Decide whether a chart should be rendered for the given stage.

    Args:
        configuration: Effective run configuration.
        stage: One of ``generate``, ``update``, ``review``, ``consolidate``.

    Returns:
        True when visualization is enabled and either every-iteration mode is
        on or this is the final (post-consolidation) render.
    """
    if not configuration.visualization_enabled:
        return False
    if configuration.visualization_every_iteration:
        return True
    return stage == "consolidate"


async def render_taxonomy_pca(
    configuration: Configuration,
    clusters: List[Dict],
    vectors_by_value: Dict[str, "np.ndarray"],
    stage: str,
    iteration_index: int,
    embedding_dimensionality: Optional[int] = None,
) -> Optional[Path]:
    """Render one PCA chart of the given taxonomy iteration's values.

    Args:
        configuration: Effective run configuration.
        clusters: The taxonomy iteration (list of cluster dicts with values).
        vectors_by_value: Full-dimensional embedding vector per value id.
        stage: One of ``generate`` / ``update`` / ``review`` / ``consolidate``.
        iteration_index: Iteration number used in the filename.
        embedding_dimensionality: Info-only; inferred from vectors when omitted.

    Returns:
        The path of the written PNG, or None when rendering was skipped or
        failed (never raises — visualization must not break a pipeline run).
    """
    if not should_render(configuration, stage):
        return None

    points = _collect_value_points(clusters)
    if len(points) < 3:
        logger.debug("Skipping PCA render for stage=%s — %d values (<3) is not plottable", stage, len(points))
        return None

    vectors = []
    kept_points = []
    for point in points:
        vec = vectors_by_value.get(point["value_id"])
        if vec is not None:
            vectors.append(np.asarray(vec, dtype=float))
            kept_points.append(point)
    if len(kept_points) < 3:
        logger.debug("Skipping PCA render for stage=%s — only %d embedded values found", stage, len(kept_points))
        return None

    matrix = np.vstack(vectors)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from pca import pca as ErdogantPCA
    except ImportError as e:
        logger.warning("PCA rendering skipped — missing optional dependency: %s", e)
        return None

    n_dims = int(configuration.visualization_dimensions or 2)
    n_components = min(n_dims, matrix.shape[0], matrix.shape[1])
    if n_components < 2:
        logger.debug("Skipping PCA render — not enough components for a chart")
        return None

    try:
        pca_model = ErdogantPCA(n_components=n_components)
        result = pca_model.fit_transform(matrix)
        projected = np.asarray(result["PC"].values if hasattr(result["PC"], "values") else result["PC"])
        # print(result)
        explained = np.asarray( # "explained_var" or "variance_ratio"
            result["explained_var"].values
            if hasattr(result["explained_var"], "values")
            else result["explained_var"]
        )
    except Exception as e:
        logger.warning("PCA fit failed for stage=%s iteration=%d: %s", stage, iteration_index, e)
        return None

    variance_share = float(np.sum(explained)) if explained.size else 0.0

    # Assign one color per dimension.
    dim_ids = sorted({p["dimension_id"] for p in kept_points})
    dim_index = {d: i for i, d in enumerate(dim_ids)}
    cmap = plt.get_cmap("tab10" if len(dim_ids) <= 10 else "tab20")
    colors = [cmap(dim_index[p["dimension_id"]] % cmap.N) for p in kept_points]

    fig = plt.figure(figsize=(9, 7))
    if n_components >= 3:
        ax = fig.add_subplot(projection="3d")
        ax.scatter(projected[:, 0], projected[:, 1], projected[:, 2], c=colors, s=48, alpha=0.85)
        ax.set_zlabel("PC3")
    else:
        ax = fig.add_subplot()
        ax.scatter(projected[:, 0], projected[:, 1], c=colors, s=48, alpha=0.85)
        # Label each point with its value id (small) for merge debugging.
        for i, point in enumerate(kept_points):
            ax.annotate(
                point["value_id"],
                (projected[i, 0], projected[i, 1]),
                fontsize=7,
                alpha=0.7,
                xytext=(3, 3),
                textcoords="offset points",
            )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")

    weak_proxy = " (weak proxy — low captured variance)" if variance_share < 0.5 else ""
    ax.set_title(
        f"Taxonomy values by dimension — stage: {stage}, iteration: {iteration_index}\n"
        f"Explained variance (top {n_components} PCs): {variance_share:.0%}{weak_proxy}"
    )

    # Legend of dimensions.
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", color=cmap(dim_index[d] % cmap.N),
                   label=f"{d}: {next(p['dimension_name'] for p in kept_points if p['dimension_id'] == d)}")
        for d in dim_ids
    ]
    ax.legend(handles=handles, fontsize=8, loc="best")

    out_dir = resolve_output_dir(configuration)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (
        f"taxonomy_pca_{_sanitize_name(configuration.name)}_{stage}_{iteration_index}.png"
    )

    try:
        fig.tight_layout()
        fig.savefig(out_path, dpi=140)
    except Exception as e:
        logger.warning("PCA chart save failed for stage=%s: %s", stage, e)
        return None
    finally:
        plt.close(fig)

    logger.info("PCA chart written: %s (explained variance %.0f%%)", out_path, variance_share)
    return out_path