"""Taxonomy biplot visualization utility (erdogant/pca based).

Renders PCA **biplots** of a taxonomy: *value* points positioned on their
*dimension* axes (loading arrows) — a debugging/explanation view of the
axial-coding structure.

Axis semantics
--------------
The design matrix ``X`` has one **row per value** and one **column per
dimension**. A value's entry in its own dimension's column encodes its
position along that axis:

- ``embeddings`` mode (consolidation enabled): positions come from the same
  embedding geometry used by value consolidation. Within each dimension, the
  pairwise embedding distances are reduced to a 1-D ordering via classical
  (Torgerson) MDS — double-centering + leading eigenvector — and normalized
  so the largest magnitude is 1. Relative separations between sibling values
  are preserved.
- ``uniform`` mode (consolidation disabled): every value of a dimension sits
  at a unitary coordinate ``1.0`` on its axis (pure one-hot row).

All other columns are zero, so a value's PCA score lies along its dimension's
loading direction at a distance reflecting its axis position.

Caveats built in (TAXONOMY_QUALITY_PLAN.md §7):

- **Merge decisions are never made from projected coordinates.** Only the
  full-dimensional distance computed during consolidation decides merges.
  PCA is a lossy linear projection; two points can look close in projection
  while being far apart in the full embedding space, or vice versa.
- Every chart reports the **explained variance ratio**. When 2–3 components
  capture a low share of total variance, the plot is a weak proxy for true
  distance and is labeled as such.

This is a shared utility, not a graph node, because an "iteration" spans
multiple node types. It is called (optionally) from ``generate_taxonomy``,
``update_taxonomy``, ``review_taxonomy``, and ``consolidate_values`` behind
the ``visualization.enabled`` config flag, and directly by the standalone
``--visualize`` CLI command — off by default, no latency/cost on normal runs.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)


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
                    "description": value.get("description", ""),
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
        stage: One of ``generate``, ``update``, ``review``, ``consolidate``,
            ``standalone``.

    Returns:
        True when visualization is enabled and either every-iteration mode is
        on or this is a final render (post-consolidation / standalone).
    """
    if not configuration.visualization_enabled:
        return False
    if configuration.visualization_every_iteration:
        return True
    return stage in ("consolidate", "standalone")


def _mds_1d(dist_matrix: np.ndarray) -> np.ndarray:
    """Classical (Torgerson) MDS to one dimension.

    Double-centers the squared distance matrix and returns the leading
    eigenvector scaled by the square root of its eigenvalue. Falls back to
    index positions if the eigen-decomposition is unusable.
    """
    d2 = np.square(np.asarray(dist_matrix, dtype=float))
    row_mean = d2.mean(axis=1, keepdims=True)
    col_mean = d2.mean(axis=0, keepdims=True)
    grand_mean = d2.mean()
    b = -0.5 * (d2 - row_mean - col_mean + grand_mean)
    b = (b + b.T) / 2.0  # symmetrize for numerical safety
    try:
        eigenvalues, eigenvectors = np.linalg.eigh(b)
    except np.linalg.LinAlgError:
        return np.arange(d2.shape[0], dtype=float)
    leading = int(np.argmax(eigenvalues))
    coords = eigenvectors[:, leading] * np.sqrt(max(float(eigenvalues[leading]), 0.0))
    if not np.all(np.isfinite(coords)):
        return np.arange(d2.shape[0], dtype=float)
    return coords


def _resolve_axis_positions(configuration: Configuration, axis_positions: str) -> str:
    """Resolve the requested axis-position mode to a concrete one.

    ``auto`` follows the consolidation setting: embeddings when consolidation
    is enabled (geometry consistent with merging), uniform otherwise.
    """
    if axis_positions in ("uniform", "embeddings"):
        return axis_positions
    return "embeddings" if configuration.consolidate_values else "uniform"


async def build_axis_matrix(
    points: List[Dict],
    mode: str,
    configuration: Configuration,
) -> Tuple[np.ndarray, List[Dict]]:
    """Build the ``(n_values x n_dimensions)`` matrix of axis coordinates.

    Each dimension is one column; a value's row carries its 1-D position on
    its own dimension's axis and zeros elsewhere. See the module docstring
    for the semantics of each mode. Never raises — falls back to uniform
    positions when embeddings are unavailable.
    """
    dim_ids = sorted({p["dimension_id"] for p in points})
    dim_index = {d: i for i, d in enumerate(dim_ids)}
    dims = [
        {
            "id": d,
            "name": next(p["dimension_name"] for p in points if p["dimension_id"] == d),
        }
        for d in dim_ids
    ]
    matrix = np.zeros((len(points), len(dim_ids)), dtype=float)

    if mode == "uniform":
        for row, point in enumerate(points):
            matrix[row, dim_index[point["dimension_id"]]] = 1.0
        return matrix, dims

    from taxonomy_generator.utils import (
        l2_normalize,
        load_embeddings_model,
        pairwise_euclidean,
    )

    texts = [
        f"{p['label']}. {p.get('description', '')}".strip(". ") for p in points
    ]
    try:
        embeddings = load_embeddings_model(configuration.embedding)
        raw = np.asarray(await embeddings.aembed_documents(texts), dtype=float)
    except Exception as e:
        logger.warning(
            "Embedding failed for axis positions — falling back to uniform: %s", e
        )
        for row, point in enumerate(points):
            matrix[row, dim_index[point["dimension_id"]]] = 1.0
        return matrix, dims

    vectors = l2_normalize(raw)

    rows_by_dim: Dict[str, List[int]] = {}
    for row, point in enumerate(points):
        rows_by_dim.setdefault(point["dimension_id"], []).append(row)

    for dim_id, rows in rows_by_dim.items():
        col = dim_index[dim_id]
        if len(rows) == 1:
            # A single value on the axis sits at the unit position.
            matrix[rows[0], col] = 1.0
            continue
        dist = pairwise_euclidean(vectors[rows])
        coords = _mds_1d(dist)
        max_abs = float(np.max(np.abs(coords)))
        if max_abs > 0:
            coords = coords / max_abs  # largest magnitude becomes ±1
        matrix[rows, col] = coords

    return matrix, dims


def export_axis_matrix_csv(
    configuration: Configuration,
    points: List[Dict],
    matrix: np.ndarray,
    dims: List[Dict],
    stage: str,
    iteration_index: int,
    mode: str,
) -> Optional[Path]:
    """Export the axis-coordinate design matrix to CSV next to the chart.

    The CSV carries identifying columns (``value_id``, ``dimension_id``,
    ``label``) followed by one column per dimension — the exact vectors
    fed to PCA — so the projection can be inspected or reproduced
    externally. Fail-soft: never raises, returns None on failure.
    """
    out_dir = resolve_output_dir(configuration)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (
        f"taxonomy_vectors_{_sanitize_name(configuration.name)}_{stage}_{iteration_index}.csv"
    )
    try:
        import pandas as pd

        frame = pd.DataFrame(
            matrix,
            columns=[
                f"dim_{d['id']}_{_sanitize_name(str(d['name']))}" for d in dims
            ],
        )
        frame.insert(0, "value_id", [p["value_id"] for p in points])
        frame.insert(1, "dimension_id", [p["dimension_id"] for p in points])
        frame.insert(2, "label", [p["label"] for p in points])
        frame.to_csv(out_path, index=False)
    except Exception as e:
        logger.warning("Axis-matrix CSV export failed for stage=%s: %s", stage, e)
        return None
    logger.info("PCA vectors written: %s (axis positions: %s)", out_path, mode)
    return out_path


def _extract_loadings(result, n_features: int, n_components: int) -> Optional[np.ndarray]:
    """Extract a ``(n_features x n_components)`` loadings matrix from a pca result."""
    loadings = None
    if isinstance(result, dict):
        raw = result.get("loadings")
        if raw is not None:
            loadings = np.asarray(raw.values if hasattr(raw, "values") else raw, dtype=float)
        else:
            model = result.get("model")
            components = getattr(model, "components_", None)
            if components is not None:
                loadings = np.asarray(components, dtype=float).T
    if loadings is None:
        return None
    # Orient as (features x components) regardless of the source layout.
    if loadings.shape == (n_components, n_features):
        loadings = loadings.T
    return loadings if loadings.shape == (n_features, n_components) else None


async def render_taxonomy_biplot(
    configuration: Configuration,
    clusters: List[Dict],
    stage: str,
    iteration_index: int,
    axis_positions: str = "auto",
) -> Optional[Path]:
    """Render one PCA biplot of the given taxonomy iteration's values.

    Values are points placed on their dimension axes (loading arrows) of the
    PCA projection of the axis-coordinate matrix (see module docstring).

    Args:
        configuration: Effective run configuration.
        clusters: The taxonomy iteration (list of cluster dicts with values).
        stage: One of ``generate`` / ``update`` / ``review`` / ``consolidate``
            / ``standalone``.
        iteration_index: Iteration number used in the filename.
        axis_positions: ``auto`` / ``embeddings`` / ``uniform`` — see
            ``_resolve_axis_positions``.

    Returns:
        The path of the written PNG, or None when rendering was skipped or
        failed (never raises — visualization must not break a pipeline run).
    """
    if not should_render(configuration, stage):
        return None

    points = _collect_value_points(clusters)
    if len(points) < 3:
        logger.debug("Skipping biplot render for stage=%s — %d values (<3) is not plottable", stage, len(points))
        return None

    mode = _resolve_axis_positions(configuration, axis_positions)
    matrix, dims = await build_axis_matrix(points, mode, configuration)

    # Export the exact PCA input vectors to CSV for external inspection.
    export_axis_matrix_csv(
        configuration, points, matrix, dims, stage, iteration_index, mode
    )

    if matrix.shape[1] < 2:
        logger.debug("Skipping biplot render — a single dimension gives a 1-D space")
        return None

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from pca import pca as ErdogantPCA
    except ImportError as e:
        logger.warning("Biplot rendering skipped — missing optional dependency: %s", e)
        return None

    n_dims = int(configuration.visualization_dimensions or 2)
    n_components = min(n_dims, matrix.shape[0], matrix.shape[1])
    if n_components < 2:
        logger.debug("Skipping biplot render — not enough components for a chart")
        return None

    try:
        pca_model = ErdogantPCA(n_components=n_components, normalize=False)
        result = pca_model.fit_transform(matrix)
        projected = np.asarray(result["PC"].values if hasattr(result["PC"], "values") else result["PC"])
        explained = np.asarray(  # "explained_var" or "variance_ratio"
            result["explained_var"].values
            if hasattr(result["explained_var"], "values")
            else result["explained_var"]
        )
    except Exception as e:
        logger.warning("PCA fit failed for stage=%s iteration=%d: %s", stage, iteration_index, e)
        return None

    ratio_raw = result.get("variance_ratio")
    if ratio_raw is not None:
        ratios = np.asarray(
            ratio_raw.values if hasattr(ratio_raw, "values") else ratio_raw, dtype=float
        )
        variance_share = float(np.sum(ratios)) if ratios.size else 0.0
    else:
        variance_share = float(explained[-1]) if explained.size else 0.0
    loadings = _extract_loadings(result, matrix.shape[1], n_components)

    # Assign one color per dimension.
    dim_ids = [d["id"] for d in dims]
    cmap = plt.get_cmap("tab10" if len(dim_ids) <= 10 else "tab20")
    dim_colors = {d: cmap(i % cmap.N) for i, d in enumerate(dim_ids)}
    colors = [dim_colors[p["dimension_id"]] for p in points]

    # Display-only jitter so coincident points (uniform mode collapses every
    # value of a dimension onto the same projected point) stay legible.
    # Seeded by random_seed for reproducibility; the data itself is untouched.
    offsets = np.zeros_like(projected, dtype=float)
    if mode == "uniform" and len(projected) > 0:
        rng = np.random.default_rng(configuration.random_seed if configuration.random_seed is not None else 0)
        spans = np.maximum(
            projected.max(axis=0) - projected.min(axis=0), np.finfo(float).eps
        )
        offsets = rng.uniform(-0.03, 0.03, size=projected.shape) * spans

    fig = plt.figure(figsize=(9, 7))
    if n_components >= 3:
        ax = fig.add_subplot(projection="3d")
        ax.scatter(
            projected[:, 0] + offsets[:, 0],
            projected[:, 1] + offsets[:, 1],
            projected[:, 2] + offsets[:, 2],
            c=colors, s=48, alpha=0.85,
        )
        ax.set_zlabel("PC3")
    else:
        ax = fig.add_subplot()
        ax.scatter(projected[:, 0] + offsets[:, 0], projected[:, 1] + offsets[:, 1], c=colors, s=48, alpha=0.85)
        for i, point in enumerate(points):
            ax.annotate(
                point["value_id"],
                (projected[i, 0] + offsets[i, 0], projected[i, 1] + offsets[i, 1]),
                fontsize=7,
                alpha=0.7,
                xytext=(3, 3),
                textcoords="offset points",
            )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")

    # Dimension loading arrows (biplot). Scaled to a fraction of the score
    # spread so arrows and points share the same visual frame.
    if loadings is not None:
        max_radius = float(np.max(np.linalg.norm(projected, axis=1))) if len(projected) else 0.0
        max_arrow = float(np.max(np.linalg.norm(loadings, axis=1))) if loadings.size else 0.0
        if max_arrow > 0 and max_radius > 0:
            scale = 0.7 * max_radius / max_arrow
            arrows = loadings * scale
            for i, dim in enumerate(dims):
                color = dim_colors[dim["id"]]
                label = f"{dim['id']}: {dim['name']}"
                if len(label) > 30:
                    label = label[:27] + "..."
                if n_components >= 3:
                    ax.quiver(
                        0, 0, 0, arrows[i, 0], arrows[i, 1], arrows[i, 2],
                        color=color, linewidth=1.6, arrow_length_ratio=0.08,
                    )
                    ax.text(arrows[i, 0], arrows[i, 1], arrows[i, 2], label, fontsize=8, color=color)
                else:
                    ax.annotate(
                        "",
                        xy=(arrows[i, 0], arrows[i, 1]),
                        xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.6),
                    )
                    ax.annotate(
                        label,
                        (arrows[i, 0], arrows[i, 1]),
                        fontsize=8,
                        color=color,
                        fontweight="bold",
                        xytext=(4, 4),
                        textcoords="offset points",
                    )

    weak_proxy = " (weak proxy — low captured variance)" if variance_share < 0.5 else ""
    ax.set_title(
        f"Taxonomy biplot — values on dimension axes — stage: {stage}, iteration: {iteration_index}\n"
        f"Axis positions: {mode} · Explained variance (top {n_components} PCs): {variance_share:.0%}{weak_proxy}"
    )

    # Legend of dimensions.
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", color=dim_colors[d["id"]],
                   label=f"{d['id']}: {d['name']}")
        for d in dims
    ]
    ax.legend(handles=handles, fontsize=8, loc="best")

    out_dir = resolve_output_dir(configuration)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (
        f"taxonomy_biplot_{_sanitize_name(configuration.name)}_{stage}_{iteration_index}.png"
    )

    try:
        fig.tight_layout()
        fig.savefig(out_path, dpi=140)
    except Exception as e:
        logger.warning("Biplot save failed for stage=%s: %s", stage, e)
        return None
    finally:
        plt.close(fig)

    logger.info("Biplot written: %s (axis positions: %s, explained variance %.0f%%)", out_path, mode, variance_share * 100)
    return out_path