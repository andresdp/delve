"""Taxonomy biplot visualization utility (erdogant/pca + Plotly based).

Renders interactive **biplots** of a taxonomy: *value* points positioned on
their *dimension* axes — a debugging/explanation view of the axial-coding
structure. Two rendering paths, chosen by dimension count vs.
``visualization.dimensions``:

- **Exact** (``_render_direct_scatter``): when the taxonomy has no more
  dimensions than the configured chart size, each axis is one taxonomy
  dimension, plotted directly — no projection, nothing lossy.
- **PCA-reduced** (``_render_pca_biplot``): otherwise, the axis-coordinate
  matrix is reduced via ``erdogant/pca`` to the configured number of
  components, same as before. What changed is how the reduction is *drawn*:
  each dimension's loading direction becomes one axis of a shared, fixed
  radius, extending both ways through the origin (rather than a one-way
  arrow scaled to its own data-dependent magnitude), and values are placed
  on their own dimension's axis at a distance reflecting their axis
  coordinate. The PCA fit itself is untouched — it still decides each
  dimension's meaningful angle relative to the others; only the loading's
  magnitude is discarded in favor of a shared radius.

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

All other columns are zero, so a value's plotted position lies along its
dimension's axis at a distance reflecting its axis position. Values whose
own-axis coordinate lands at/near zero are nudged outward to a minimum
radius (``_avoid_origin_matrix``) so they don't render on top of every other
dimension's zero-valued values at the shared origin — display-only, the
exported CSV keeps the untouched coordinates.

Caveats built in (TAXONOMY_QUALITY_PLAN.md §7):

- **Merge decisions are never made from projected coordinates.** Only the
  full-dimensional distance computed during consolidation decides merges.
  PCA is a lossy linear projection; two points can look close in projection
  while being far apart in the full embedding space, or vice versa.
- The PCA-reduced chart reports the **explained variance ratio**. When the
  chosen components capture a low share of total variance, the plot is a
  weak proxy for true distance and is labeled as such.

Every chart is an interactive, self-contained HTML file (Plotly): hovering a
value shows its full id/label/description/dimension, and the legend toggles
a dimension's points on click.

This is a shared utility, not a graph node, because an "iteration" spans
multiple node types. It is called (optionally) from ``generate_taxonomy``,
``update_taxonomy``, ``review_taxonomy``, and ``consolidate_values`` behind
the ``visualization.enabled`` config flag, and directly by the standalone
``--visualize`` CLI command — off by default, no latency/cost on normal runs.
"""

import logging
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from taxonomy_generator.configuration import Configuration

logger = logging.getLogger(__name__)

# Below this, a PCA loading is treated as genuinely zero (not a rounding
# artifact) — the axis matrix's columns are exactly orthogonal by
# construction, so unrepresented dimensions land many orders of magnitude
# below this in practice.
MIN_LOADING_NORM = 1e-6


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
    ``label``) followed by one column per dimension — the exact axis-
    coordinate vectors (PCA input when reduction applies) — so the chart can
    be inspected or reproduced externally. Fail-soft: never raises, returns
    None on failure.
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
    logger.info("Axis vectors written: %s (axis positions: %s)", out_path, mode)
    return out_path


def _avoid_origin_matrix(
    matrix: np.ndarray,
    points: List[Dict[str, Any]],
    dims: List[Dict[str, Any]],
    min_fraction: float = 0.15,
) -> np.ndarray:
    """Nudge each value's own-axis coordinate away from the shared origin.

    Values whose axis coordinate lands at/near 0 would otherwise render on
    top of every other dimension's zero-valued values at the shared center
    point. Remaps each value's own-dimension coordinate to
    ``sign * (min_fraction + (1 - min_fraction) * abs(value))`` — exact zero
    deterministically maps to ``+min_fraction`` — preserving sign and
    relative order within the dimension.

    Display-only: returns a copy, so the raw matrix (e.g. the exported CSV
    and the PCA fit) stays untouched.
    """
    dim_index = {d["id"]: i for i, d in enumerate(dims)}
    out = matrix.copy()
    for row, point in enumerate(points):
        col = dim_index[point["dimension_id"]]
        value = matrix[row, col]
        sign = 1.0 if value >= 0 else -1.0
        out[row, col] = sign * (min_fraction + (1 - min_fraction) * abs(value))
    return out


def _point_label(point: Dict, max_len: int = 25) -> str:
    """Annotation text for a value point: ``id: Label`` (truncated)."""
    label = str(point.get("label", "")).strip()
    text = f"{point['value_id']}: {label}" if label else str(point["value_id"])
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


def _hover_text(point: Dict[str, Any], dim_name: str) -> str:
    """Full, untruncated hover text: id, label, description, dimension."""
    label = str(point.get("label", "")).strip()
    description = str(point.get("description", "")).strip()
    lines = [f"<b>{point.get('value_id', '?')}</b>: {label}"]
    if description:
        lines.append(description)
    lines.append(f"<i>Dimension {point.get('dimension_id', '?')}: {dim_name}</i>")
    return "<br>".join(lines)


def _axis_angle_degrees(dx: float, dy: float) -> float:
    """Text rotation (degrees) so a label crosses its axis at 90°, never upside-down.

    2D only — used for dimension-name and value labels so they read across
    their own axis rather than overlapping it lengthwise. Normalized to
    ``(-90, 90]`` so text is always upright.
    """
    angle = -math.degrees(math.atan2(dy, dx)) + 90.0
    if angle > 90:
        angle -= 180
    elif angle <= -90:
        angle += 180
    return angle


def _dimension_color_map(dims: List[Dict[str, Any]]) -> Dict[str, str]:
    """Assign one color per dimension (Plotly qualitative palette)."""
    import plotly.express as px

    palette = (
        px.colors.qualitative.Plotly if len(dims) <= 10 else px.colors.qualitative.Alphabet
    )
    return {d["id"]: palette[i % len(palette)] for i, d in enumerate(dims)}


def _uniform_mode_jitter(configuration: Configuration, coords: np.ndarray, mode: str) -> np.ndarray:
    """Display-only jitter so coincident points stay legible in uniform mode.

    Uniform mode collapses every value of a dimension onto the same
    coordinate, so without jitter they'd overplot exactly. Seeded by
    ``random_seed`` for reproducibility; the underlying data is untouched.
    """
    offsets = np.zeros_like(coords, dtype=float)
    if mode == "uniform" and len(coords) > 0:
        rng = np.random.default_rng(configuration.random_seed if configuration.random_seed is not None else 0)
        spans = np.maximum(coords.max(axis=0) - coords.min(axis=0), np.finfo(float).eps)
        offsets = rng.uniform(-0.03, 0.03, size=coords.shape) * spans
    return offsets


def _save_biplot_html(
    fig: Any, configuration: Configuration, stage: str, iteration_index: int, kind: str, n_dims: int
) -> Optional[Path]:
    """Save a rendered figure to the standard biplot filename. Fail-soft."""
    out_dir = resolve_output_dir(configuration)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (
        f"taxonomy_biplot_{_sanitize_name(configuration.name)}_{stage}_{iteration_index}_{n_dims}d.html"
    )
    try:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)
    except Exception as e:
        logger.warning("%s save failed for stage=%s: %s", kind, stage, e)
        return None
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


def _render_direct_scatter(
    configuration: Configuration,
    points: List[Dict[str, Any]],
    matrix: np.ndarray,
    dims: List[Dict[str, Any]],
    stage: str,
    iteration_index: int,
    mode: str,
) -> Optional[Path]:
    """Plot values directly on the taxonomy's own dimension axes — no PCA.

    Used when the taxonomy has no more dimensions than the configured chart
    size (``visualization.dimensions``): the axis-coordinate matrix already
    has one column per dimension, so there is nothing to reduce. Plotting
    the raw columns is exact (not a lossy projection), and each axis is
    directly readable as one named dimension rather than an abstract,
    rotated principal component.
    """
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        logger.warning("Scatter rendering skipped — missing optional dependency: %s", e)
        return None

    n_axis_dims = matrix.shape[1]
    dim_colors = _dimension_color_map(dims)
    offsets = _uniform_mode_jitter(configuration, matrix, mode)
    # 2D only: dimension 0 is the horizontal axis, dimension 1 is the
    # vertical axis — labels are rotated to cross their own axis at 90°
    # (vertical text on the horizontal axis, horizontal text on the
    # vertical axis) so they never overlap each other.
    axis_angles = {dims[0]["id"]: 90.0, dims[1]["id"]: 0.0} if n_axis_dims == 2 else {}
    annotations = []

    fig = go.Figure()
    for dim in dims:
        idxs = [row for row, p in enumerate(points) if p["dimension_id"] == dim["id"]]
        if not idxs:
            continue
        color = dim_colors[dim["id"]]
        xs = matrix[idxs, 0] + offsets[idxs, 0]
        ys = matrix[idxs, 1] + offsets[idxs, 1]
        hover = [_hover_text(points[row], dim["name"]) for row in idxs]
        if n_axis_dims >= 3:
            zs = matrix[idxs, 2] + offsets[idxs, 2]
            labels = [_point_label(points[row]) for row in idxs]
            fig.add_trace(go.Scatter3d(
                x=xs, y=ys, z=zs, mode="markers+text",
                marker=dict(color=color, size=5),
                text=labels, textfont=dict(size=8),
                hovertext=hover, hoverinfo="text",
                name=f"{dim['id']}: {dim['name']}",
            ))
        else:
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers",
                marker=dict(color=color, size=9),
                hovertext=hover, hoverinfo="text",
                name=f"{dim['id']}: {dim['name']}",
            ))
            angle = axis_angles[dim["id"]]
            for row, x, y in zip(idxs, xs, ys):
                annotations.append(dict(
                    x=x, y=y, text=_point_label(points[row]), textangle=angle,
                    showarrow=False, font=dict(size=8, color=color),
                    xanchor="center", yanchor="bottom", yshift=6,
                ))
            tip_x, tip_y = (matrix[:, 0].max() * 1.1, 0) if dim["id"] == dims[0]["id"] else (0, matrix[:, 1].max() * 1.1)
            annotations.append(dict(
                x=tip_x, y=tip_y, text=f"{dim['id']}: {dim['name']}", textangle=angle,
                showarrow=False, font=dict(size=10, color=color),
            ))

    if annotations:
        fig.update_layout(annotations=annotations)

    title = (
        f"Taxonomy scatter — values on their own dimension axes — stage: {stage}, iteration: {iteration_index}<br>"
        f"<sup>Axis positions: {mode} · {n_axis_dims} dimensions plotted directly (no PCA — nothing to reduce)</sup>"
    )
    if n_axis_dims >= 3:
        fig.update_layout(
            title=title,
            template="plotly_white",
            scene=dict(
                xaxis_title=f"{dims[0]['id']}: {dims[0]['name']}",
                yaxis_title=f"{dims[1]['id']}: {dims[1]['name']}",
                zaxis_title=f"{dims[2]['id']}: {dims[2]['name']}",
            ),
        )
    else:
        # Dimension names are already drawn as rotated axis-tip annotations
        # above; the zero-lines themselves double as each dimension's axis,
        # colored and thickened to match (mirrors the PCA biplot's axes).
        fig.update_layout(
            title=title,
            template="plotly_white",
            xaxis=dict(zeroline=True, zerolinewidth=3, zerolinecolor=dim_colors[dims[0]["id"]]),
            yaxis=dict(zeroline=True, zerolinewidth=3, zerolinecolor=dim_colors[dims[1]["id"]]),
        )

    out_path = _save_biplot_html(fig, configuration, stage, iteration_index, kind="Scatter", n_dims=n_axis_dims)
    if out_path is not None:
        logger.info("Scatter written: %s (axis positions: %s, %d dimensions, no PCA)", out_path, mode, n_axis_dims)
    return out_path


def _render_pca_biplot(
    configuration: Configuration,
    points: List[Dict[str, Any]],
    matrix: np.ndarray,
    display_matrix: np.ndarray,
    dims: List[Dict[str, Any]],
    stage: str,
    iteration_index: int,
    mode: str,
    n_target: int,
) -> Optional[Path]:
    """PCA-reduce the axis matrix, then plot on equal-radius, bidirectional axes.

    The PCA fit runs on the raw ``matrix`` (unaffected by origin-avoidance)
    so the resulting loading directions reflect the true geometry. Each
    dimension's loading is then unit-normalized — direction kept, magnitude
    discarded — and drawn as a full line of shared radius through the
    origin. Values are placed on their own dimension's axis at a distance
    given by their origin-avoided coordinate (``display_matrix``), not by
    their raw PCA-projected score, so every value sits exactly on its own
    axis regardless of how much that dimension's loading originally weighed.
    """
    try:
        from pca import pca as ErdogantPCA
    except ImportError as e:
        logger.warning("Biplot rendering skipped — missing optional dependency: %s", e)
        return None
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        logger.warning("Biplot rendering skipped — missing optional dependency: %s", e)
        return None

    n_components = min(n_target, matrix.shape[0], matrix.shape[1])
    if n_components < 2:
        logger.debug("Skipping biplot render — not enough components for a chart")
        return None

    try:
        pca_model = ErdogantPCA(n_components=n_components, normalize=False)
        result = pca_model.fit_transform(matrix)
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
        explained_raw = result.get("explained_var")
        explained = (
            np.asarray(explained_raw.values if hasattr(explained_raw, "values") else explained_raw, dtype=float)
            if explained_raw is not None
            else np.array([])
        )
        variance_share = float(explained[-1]) if explained.size else 0.0

    loadings = _extract_loadings(result, matrix.shape[1], n_components)
    if loadings is None:
        logger.warning("PCA loadings unavailable for stage=%s iteration=%d — skipping biplot render", stage, iteration_index)
        return None

    # This axis matrix is block-orthogonal by construction (each value's row
    # is nonzero only in its own dimension's column), so PCA routinely gives
    # some dimensions a genuinely ~0 loading in the chosen components — not
    # a rounding artifact, a real "not represented in this projection"
    # result. Those dimensions get no axis/points (nothing meaningful to
    # draw); they're still named in the legend so nothing silently vanishes.
    norms = np.linalg.norm(loadings, axis=1)
    active_mask = norms > MIN_LOADING_NORM
    unit_directions = np.zeros_like(loadings)
    unit_directions[active_mask] = loadings[active_mask] / norms[active_mask, None]

    dim_index = {d["id"]: i for i, d in enumerate(dims)}
    active_dims = [d for d, keep in zip(dims, active_mask) if keep]
    omitted_dims = [d for d, keep in zip(dims, active_mask) if not keep]
    active_ids = {d["id"] for d in active_dims}

    radius = 1.0
    active_row_mask = np.array([p["dimension_id"] in active_ids for p in points])
    active_points = [p for p, keep in zip(points, active_row_mask) if keep]
    active_display = display_matrix[active_row_mask]
    plotted = np.zeros((len(active_points), n_components))
    for i, point in enumerate(active_points):
        col = dim_index[point["dimension_id"]]
        plotted[i] = active_display[i, col] * radius * unit_directions[col]

    offsets = _uniform_mode_jitter(configuration, plotted, mode)
    dim_colors = _dimension_color_map(dims)
    annotations = []

    fig = go.Figure()

    # Axis lines: full diameters, shared radius, solid, thick, one per active dimension.
    for dim in active_dims:
        direction = unit_directions[dim_index[dim["id"]]]
        color = dim_colors[dim["id"]]
        if n_components >= 3:
            fig.add_trace(go.Scatter3d(
                x=[-radius * direction[0], radius * direction[0]],
                y=[-radius * direction[1], radius * direction[1]],
                z=[-radius * direction[2], radius * direction[2]],
                mode="lines",
                line=dict(color=color, width=5),
                hoverinfo="skip", showlegend=False,
            ))
            # Scene axis titles are hidden (they'd just read "PC1/PC2/PC3"),
            # so the dimension name is placed as text at its own axis tip.
            fig.add_trace(go.Scatter3d(
                x=[radius * 1.08 * direction[0]],
                y=[radius * 1.08 * direction[1]],
                z=[radius * 1.08 * direction[2]],
                mode="text",
                text=[f"{dim['id']}: {dim['name']}"],
                textfont=dict(size=10, color=color),
                hoverinfo="skip", showlegend=False,
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[-radius * direction[0], radius * direction[0]],
                y=[-radius * direction[1], radius * direction[1]],
                mode="lines",
                line=dict(color=color, width=3),
                hoverinfo="skip", showlegend=False,
            ))
            angle = _axis_angle_degrees(direction[0], direction[1])
            annotations.append(dict(
                x=radius * 1.08 * direction[0], y=radius * 1.08 * direction[1],
                text=f"{dim['id']}: {dim['name']}", textangle=angle,
                showarrow=False, font=dict(size=10, color=color),
            ))

    # Value points: one trace per active dimension (color + legend + click-to-toggle).
    for dim in active_dims:
        idxs = [i for i, p in enumerate(active_points) if p["dimension_id"] == dim["id"]]
        if not idxs:
            continue
        color = dim_colors[dim["id"]]
        xs = plotted[idxs, 0] + offsets[idxs, 0]
        ys = plotted[idxs, 1] + offsets[idxs, 1]
        hover = [_hover_text(active_points[i], dim["name"]) for i in idxs]
        if n_components >= 3:
            zs = plotted[idxs, 2] + offsets[idxs, 2]
            labels = [_point_label(active_points[i]) for i in idxs]
            fig.add_trace(go.Scatter3d(
                x=xs, y=ys, z=zs, mode="markers+text",
                marker=dict(color=color, size=5),
                text=labels, textfont=dict(size=8),
                hovertext=hover, hoverinfo="text",
                name=f"{dim['id']}: {dim['name']}",
            ))
        else:
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers",
                marker=dict(color=color, size=9),
                hovertext=hover, hoverinfo="text",
                name=f"{dim['id']}: {dim['name']}",
            ))
            direction = unit_directions[dim_index[dim["id"]]]
            angle = _axis_angle_degrees(direction[0], direction[1])
            perp_x, perp_y = -direction[1] * 0.06, direction[0] * 0.06
            for i, x, y in zip(idxs, xs, ys):
                annotations.append(dict(
                    x=x + perp_x, y=y + perp_y, text=_point_label(active_points[i]), textangle=angle,
                    showarrow=False, font=dict(size=8, color=color),
                ))

    # Legend-only note for dimensions with ~0 loading in this projection —
    # nothing plotted for them, but the legend says why they're missing.
    for dim in omitted_dims:
        note = dict(
            x=[None], y=[None], mode="markers",
            marker=dict(color=dim_colors[dim["id"]], size=8, symbol="x"),
            name=f"{dim['id']}: {dim['name']} (not shown — ~0 loading here)",
            hoverinfo="skip", showlegend=True,
        )
        fig.add_trace(go.Scatter3d(z=[None], **note) if n_components >= 3 else go.Scatter(**note))

    weak_proxy = " (weak proxy — low captured variance)" if variance_share < 0.5 else ""
    omitted_note = f" · {len(omitted_dims)} of {len(dims)} dimensions not shown (see legend)" if omitted_dims else ""
    title = (
        f"Taxonomy biplot — values on equal-radius dimension axes — stage: {stage}, iteration: {iteration_index}<br>"
        f"<sup>Axis positions: {mode} · Explained variance (top {n_components} PCs): {variance_share:.0%}{weak_proxy}{omitted_note}</sup>"
    )
    if n_components >= 3:
        fig.update_layout(
            title=title,
            template="plotly_white",
            scene=dict(
                xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            ),
        )
    else:
        fig.update_layout(
            title=title,
            template="plotly_white",
            xaxis=dict(visible=False, range=[-1.3, 1.3]),
            yaxis=dict(visible=False, range=[-1.3, 1.3], scaleanchor="x"),
            annotations=annotations,
        )

    out_path = _save_biplot_html(fig, configuration, stage, iteration_index, kind="Biplot", n_dims=n_components)
    if out_path is not None:
        logger.info("Biplot written: %s (axis positions: %s, explained variance %.0f%%)", out_path, mode, variance_share * 100)
    return out_path


async def render_taxonomy_biplot(
    configuration: Configuration,
    clusters: List[Dict],
    stage: str,
    iteration_index: int,
    axis_positions: str = "auto",
) -> Optional[Path]:
    """Render one biplot of the given taxonomy iteration's values.

    Values are points placed on their own dimension's axis. When the
    taxonomy has no more dimensions than ``visualization.dimensions``, axes
    are the taxonomy's own dimensions, plotted exactly
    (``_render_direct_scatter``). Otherwise the axis-coordinate matrix is
    PCA-reduced to that many components and each dimension's loading
    direction becomes an equal-radius, bidirectional axis
    (``_render_pca_biplot``).

    Args:
        configuration: Effective run configuration.
        clusters: The taxonomy iteration (list of cluster dicts with values).
        stage: One of ``generate`` / ``update`` / ``review`` / ``consolidate``
            / ``standalone``.
        iteration_index: Iteration number used in the filename.
        axis_positions: ``auto`` / ``embeddings`` / ``uniform`` — see
            ``_resolve_axis_positions``.

    Returns:
        The path of the written HTML file, or None when rendering was
        skipped or failed (never raises — visualization must not break a
        pipeline run).
    """
    if not should_render(configuration, stage):
        return None

    points = _collect_value_points(clusters)
    if len(points) < 3:
        logger.debug("Skipping biplot render for stage=%s — %d values (<3) is not plottable", stage, len(points))
        return None

    mode = _resolve_axis_positions(configuration, axis_positions)
    matrix, dims = await build_axis_matrix(points, mode, configuration)

    # Export the exact axis-coordinate vectors to CSV for external inspection.
    export_axis_matrix_csv(
        configuration, points, matrix, dims, stage, iteration_index, mode
    )

    if matrix.shape[1] < 2:
        logger.debug("Skipping biplot render — a single dimension gives a 1-D space")
        return None

    display_matrix = _avoid_origin_matrix(matrix, points, dims)

    n_target = int(configuration.visualization_dimensions or 2)
    n_axis_dims = matrix.shape[1]

    if n_axis_dims <= n_target:
        # No more dimensions than the chart needs — nothing to reduce, plot
        # the raw (origin-avoided) axis coordinates directly.
        return _render_direct_scatter(configuration, points, display_matrix, dims, stage, iteration_index, mode)

    return _render_pca_biplot(
        configuration, points, matrix, display_matrix, dims, stage, iteration_index, mode, n_target
    )
