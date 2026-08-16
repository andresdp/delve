"""Load and validate pipeline settings from a YAML configuration file.

This module provides the central settings mechanism for Delve. It reads
``config.yaml`` (or a user-specified path), validates the values, and
exposes them as frozen dataclasses organised by concern.

Only API keys are read from environment variables / ``.env`` — all other
tunable parameters live in the YAML file.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default config path (relative to project root where main.py lives)
# ---------------------------------------------------------------------------
_DEFAULT_CONFIG_PATH = "config.yaml"


# ---------------------------------------------------------------------------
# Nested settings dataclasses (frozen = immutable after creation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelSettings:
    """LLM model configuration."""

    model: str = "openai/gpt-5.4-nano"
    fast_llm: str = "openai/gpt-5.4-nano"
    embedding: str = "openai/text-embedding-3-small"


@dataclass(frozen=True)
class PipelineSettings:
    """Pipeline execution parameters."""

    max_runs: int = 0
    sample_size: int = 0
    batch_size: int = 200
    random_seed: Optional[int] = None


@dataclass(frozen=True)
class TaxonomySettings:
    """Taxonomy generation constraints."""

    name: str = "taxonomy"
    max_num_clusters: Optional[int] = None
    cluster_name_length: int = 10
    cluster_description_length: int = 30
    suggestion_length: int = 30
    explanation_length: int = 20
    use_case: str = (
        "Generate the taxonomy that can be used to label "
        "the user intent in the conversation."
    )
    # Consecutive saturated minibatches required to stop the update loop early.
    saturation_streak_threshold: int = 2
    # Embedding-distance cutoff (Euclidean on L2-normalized vectors) below which
    # two values within the same dimension are merged automatically.
    value_merge_distance_threshold: float = 0.2
    # Distance band above the threshold routed to LLM adjudication instead of
    # auto-merge or auto-reject.
    value_merge_borderline_band: float = 0.08
    # When False, value consolidation is disabled: the consolidate_values node
    # passes the reviewed taxonomy through unchanged (no embeddings, no LLM
    # adjudication), and visualization places all values of a dimension at a
    # unitary distance on the dimension axis.
    consolidate_values: bool = True


@dataclass(frozen=True)
class SummarizationSettings:
    """Document summarization parameters."""

    skip: bool = False
    summary_length: int = 20
    explanation_length: int = 30
    max_concurrency: int = 5


@dataclass(frozen=True)
class LabelingSettings:
    """Document labeling parameters."""

    fallback_category: str = "Other"
    review_sample_size: Optional[int] = None


@dataclass(frozen=True)
class OutputSettings:
    """Output formatting parameters."""

    max_displayed_documents: int = 20
    max_docs_per_category_tree: int = 5
    content_preview_length: int = 100
    default_output_dir: str = "output"
    graph_filename: str = "graph.png"


@dataclass(frozen=True)
class VisualizationSettings:
    """PCA taxonomy visualization parameters (erdogant/pca based charts).

    All off by default so normal runs pay no extra cost/latency.
    """

    enabled: bool = False
    # If False, only render the final (post-consolidate) chart; if True,
    # render at every stage (generate/update/review/consolidate).
    every_iteration: bool = False
    # 2 or 3 dimensional projection.
    dimensions: int = 2
    # Where chart files are written (None = default_output_dir / --output).
    output_dir: Optional[str] = None


@dataclass(frozen=True)
class Settings:
    """Top-level settings container."""

    models: ModelSettings = field(default_factory=ModelSettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)
    taxonomy: TaxonomySettings = field(default_factory=TaxonomySettings)
    summarization: SummarizationSettings = field(default_factory=SummarizationSettings)
    labeling: LabelingSettings = field(default_factory=LabelingSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    visualization: VisualizationSettings = field(default_factory=VisualizationSettings)


# ---------------------------------------------------------------------------
# Helpers to build each section from the raw YAML dict
# ---------------------------------------------------------------------------

def _build_models(raw: dict) -> ModelSettings:
    return ModelSettings(
        model=raw.get("model", ModelSettings.model),
        fast_llm=raw.get("fast_llm", ModelSettings.fast_llm),
        embedding=raw.get("embedding", ModelSettings.embedding),
    )


def _build_pipeline(raw: dict) -> PipelineSettings:
    return PipelineSettings(
        max_runs=raw.get("max_runs", PipelineSettings.max_runs),
        sample_size=raw.get("sample_size", PipelineSettings.sample_size),
        batch_size=raw.get("batch_size", PipelineSettings.batch_size),
        random_seed=raw.get("random_seed", PipelineSettings.random_seed),
    )


def _build_taxonomy(raw: dict) -> TaxonomySettings:
    return TaxonomySettings(
        name=raw.get("name", TaxonomySettings.name),
        max_num_clusters=raw.get("max_num_clusters", TaxonomySettings.max_num_clusters),
        cluster_name_length=raw.get("cluster_name_length", TaxonomySettings.cluster_name_length),
        cluster_description_length=raw.get("cluster_description_length", TaxonomySettings.cluster_description_length),
        suggestion_length=raw.get("suggestion_length", TaxonomySettings.suggestion_length),
        explanation_length=raw.get("explanation_length", TaxonomySettings.explanation_length),
        use_case=raw.get("use_case", TaxonomySettings.use_case),
        saturation_streak_threshold=raw.get(
            "saturation_streak_threshold", TaxonomySettings.saturation_streak_threshold
        ),
        value_merge_distance_threshold=raw.get(
            "value_merge_distance_threshold", TaxonomySettings.value_merge_distance_threshold
        ),
        value_merge_borderline_band=raw.get(
            "value_merge_borderline_band", TaxonomySettings.value_merge_borderline_band
        ),
        consolidate_values=raw.get("consolidate_values", TaxonomySettings.consolidate_values),
    )


def _build_summarization(raw: dict) -> SummarizationSettings:
    return SummarizationSettings(
        skip=raw.get("skip", SummarizationSettings.skip),
        summary_length=raw.get("summary_length", SummarizationSettings.summary_length),
        explanation_length=raw.get("explanation_length", SummarizationSettings.explanation_length),
        max_concurrency=raw.get("max_concurrency", SummarizationSettings.max_concurrency),
    )


def _build_labeling(raw: dict) -> LabelingSettings:
    return LabelingSettings(
        fallback_category=raw.get("fallback_category", LabelingSettings.fallback_category),
        review_sample_size=raw.get("review_sample_size", LabelingSettings.review_sample_size),
    )


def _build_output(raw: dict) -> OutputSettings:
    return OutputSettings(
        max_displayed_documents=raw.get("max_displayed_documents", OutputSettings.max_displayed_documents),
        max_docs_per_category_tree=raw.get("max_docs_per_category_tree", OutputSettings.max_docs_per_category_tree),
        content_preview_length=raw.get("content_preview_length", OutputSettings.content_preview_length),
        default_output_dir=raw.get("default_output_dir", OutputSettings.default_output_dir),
        graph_filename=raw.get("graph_filename", OutputSettings.graph_filename),
    )


def _build_visualization(raw: dict) -> VisualizationSettings:
    return VisualizationSettings(
        enabled=raw.get("enabled", VisualizationSettings.enabled),
        every_iteration=raw.get("every_iteration", VisualizationSettings.every_iteration),
        dimensions=raw.get("dimensions", VisualizationSettings.dimensions),
        output_dir=raw.get("output_dir", VisualizationSettings.output_dir),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from a YAML configuration file.

    Falls back to built-in defaults when the file is missing or when
    individual keys are absent.

    Args:
        config_path: Path to the YAML file. Defaults to ``config.yaml``
            in the current working directory.

    Returns:
        A frozen ``Settings`` object.
    """
    path = Path(config_path or _DEFAULT_CONFIG_PATH)

    if not path.exists():
        logger.info("Config file not found at %s — using built-in defaults.", path)
        return Settings()

    logger.info("Loading configuration from %s", path)
    with open(path) as fh:
        raw: dict = yaml.safe_load(fh) or {}

    settings = Settings(
        models=_build_models(raw.get("models", {})),
        pipeline=_build_pipeline(raw.get("pipeline", {})),
        taxonomy=_build_taxonomy(raw.get("taxonomy", {})),
        summarization=_build_summarization(raw.get("summarization", {})),
        labeling=_build_labeling(raw.get("labeling", {})),
        output=_build_output(raw.get("output", {})),
        visualization=_build_visualization(raw.get("visualization", {})),
    )

    logger.debug("Loaded settings: %s", settings)
    return settings