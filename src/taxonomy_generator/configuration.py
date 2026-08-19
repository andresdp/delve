"""LangGraph-compatible configuration dataclass.

Reads defaults from :mod:`taxonomy_generator.settings` (YAML-backed) and
supports runtime overrides via the LangGraph ``RunnableConfig`` mechanism.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from taxonomy_generator.settings import Settings, load_settings

# Module-level cache — populated once at first import or on explicit reload.
_settings: Optional[Settings] = None


def _get_settings() -> Settings:
    """Return the cached Settings, loading from YAML on first call."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def init_settings(config_path: Optional[str] = None) -> Settings:
    """Load (or reload) settings from the given YAML path.

    Called from ``main.py`` before the pipeline starts so that the
    correct config file is used.
    """
    global _settings
    _settings = load_settings(config_path)
    return _settings


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent.

    Every field has a default derived from the YAML settings file so that
    ``Configuration()`` always works even without a ``RunnableConfig``.

    Nodes access the configuration via
    ``Configuration.from_runnable_config(config)``.
    """

    # ── Models ──────────────────────────────────────────────────────────
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=None,  # resolved lazily from Settings
        metadata={
            "description": "Main reasoning model (provider/model-name). "
            "Used for taxonomy generation and review."
        },
    )

    fast_llm: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=None,  # resolved lazily from Settings
        metadata={
            "description": "Fast/lightweight model (provider/model-name). "
            "Used for summarization, labeling, and taxonomy update."
        },
    )

    embedding: Annotated[str, {"__template_metadata__": {"kind": "embeddings"}}] = field(
        default=None,  # resolved lazily from Settings
        metadata={
            "description": "Embedding model (provider/model-name). Used for value "
            "consolidation and taxonomy PCA visualization."
        },
    )

    # ── Pipeline ────────────────────────────────────────────────────────
    max_runs: int = field(
        default=None,
        metadata={"description": "Max documents to process (0 = no limit)."},
    )

    sample_size: int = field(
        default=None,
        metadata={"description": "Sample N documents (0 = use all)."},
    )

    batch_size: int = field(
        default=None,
        metadata={"description": "Minibatch size for iterative processing."},
    )

    random_seed: Optional[int] = field(
        default=None,
        metadata={"description": "Random seed for reproducibility (null = random)."},
    )

    mode: str = field(
        default=None,
        metadata={"description": "Run mode: 'train' (build/update taxonomy) or 'test' (frozen dimensions, label only)."},
    )

    taxonomy_input: Optional[str] = field(
        default=None,
        metadata={"description": "Path to a saved taxonomy JSON used as the starting taxonomy."},
    )

    # ── Taxonomy ────────────────────────────────────────────────────────
    name: str = field(
        default=None,
        metadata={"description": "Name identifying this taxonomy."},
    )

    max_num_clusters: Optional[int] = field(
        default=None,
        metadata={"description": "Maximum number of taxonomy dimensions. None = LLM determines the count from the data."},
    )

    cluster_name_length: int = field(
        default=None,
        metadata={"description": "Max words for cluster names."},
    )

    cluster_description_length: int = field(
        default=None,
        metadata={"description": "Max words for cluster descriptions."},
    )

    suggestion_length: int = field(
        default=None,
        metadata={"description": "Max words for taxonomy suggestions."},
    )

    explanation_length: int = field(
        default=None,
        metadata={"description": "Max words for taxonomy reasoning explanations."},
    )

    use_case: str = field(
        default=None,
        metadata={"description": "Use case description guiding taxonomy generation."},
    )

    saturation_streak_threshold: int = field(
        default=None,
        metadata={"description": "Consecutive saturated minibatches required to stop the update loop early."},
    )

    value_merge_distance_threshold: float = field(
        default=None,
        metadata={"description": "Embedding-distance cutoff (epsilon) for automatic value consolidation."},
    )

    value_merge_borderline_band: float = field(
        default=None,
        metadata={"description": "Distance band above epsilon routed to LLM adjudication for value merges."},
    )

    consolidate_values: bool = field(
        default=None,
        metadata={"description": "Consolidate semantically duplicate values within dimensions (default true)."},
    )

    # ── Summarization ──────────────────────────────────────────────────
    skip_summarization: bool = field(
        default=None,
        metadata={"description": "Skip the summarization step entirely."},
    )

    summary_length: int = field(
        default=None,
        metadata={"description": "Max words for document summaries."},
    )

    summary_explanation_length: int = field(
        default=None,
        metadata={"description": "Max words for summary explanations."},
    )

    summary_max_concurrency: int = field(
        default=None,
        metadata={"description": "Max concurrent LLM requests during summarization."},
    )

    # ── Labeling ────────────────────────────────────────────────────────
    fallback_category: str = field(
        default=None,
        metadata={"description": "Fallback category when no taxonomy match."},
    )

    review_sample_size: Optional[int] = field(
        default=None,
        metadata={"description": "Review sample size (null = uses batch_size)."},
    )

    # ── Output ──────────────────────────────────────────────────────────
    max_displayed_documents: int = field(
        default=None,
        metadata={"description": "Max documents shown in rich display table."},
    )

    max_docs_per_category_tree: int = field(
        default=None,
        metadata={"description": "Max documents shown per category in the taxonomy tree view."},
    )

    content_preview_length: int = field(
        default=None,
        metadata={"description": "Characters shown in document preview."},
    )

    default_output_dir: str = field(
        default=None,
        metadata={"description": "Default directory for output files."},
    )

    graph_filename: str = field(
        default=None,
        metadata={"description": "Pipeline graph diagram filename."},
    )

    # ── Visualization ────────────────────────────────────────────────────
    visualization_enabled: bool = field(
        default=None,
        metadata={"description": "Enable taxonomy PCA chart export (default false)."},
    )

    visualization_every_iteration: bool = field(
        default=None,
        metadata={"description": "Render a PCA chart at every stage, not only post-consolidation."},
    )

    visualization_dimensions: int = field(
        default=None,
        metadata={"description": "PCA projection dimensions for charts: 2 or 3."},
    )

    visualization_output_dir: Optional[str] = field(
        default=None,
        metadata={"description": "Directory for chart files (defaults to the output dir)."},
    )

    # ── LangGraph integration ──────────────────────────────────────────

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object.

        Priority: RunnableConfig values > YAML settings > built-in defaults.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}

        settings = _get_settings()
        defaults = cls._defaults_from_settings(settings)

        _fields = {f.name for f in fields(cls) if f.init}
        kwargs = {}
        for name in _fields:
            if name in configurable and configurable[name] is not None:
                kwargs[name] = configurable[name]
            elif defaults.get(name) is not None:
                kwargs[name] = defaults[name]

        return cls(**kwargs)

    @staticmethod
    def _defaults_from_settings(s: Settings) -> dict:
        """Flatten the nested Settings into a flat dict matching field names."""
        return {
            # Models
            "model": s.models.model,
            "fast_llm": s.models.fast_llm,
            "embedding": s.models.embedding,
            # Pipeline
            "max_runs": s.pipeline.max_runs,
            "sample_size": s.pipeline.sample_size,
            "batch_size": s.pipeline.batch_size,
            "random_seed": s.pipeline.random_seed,
            # Pipeline — run modes / seeding
            "mode": s.pipeline.mode,
            "taxonomy_input": s.pipeline.taxonomy_input,
            # Taxonomy
            "name": s.taxonomy.name,
            "max_num_clusters": s.taxonomy.max_num_clusters,
            "cluster_name_length": s.taxonomy.cluster_name_length,
            "cluster_description_length": s.taxonomy.cluster_description_length,
            "suggestion_length": s.taxonomy.suggestion_length,
            "explanation_length": s.taxonomy.explanation_length,
            "use_case": s.taxonomy.use_case,
            "saturation_streak_threshold": s.taxonomy.saturation_streak_threshold,
            "value_merge_distance_threshold": s.taxonomy.value_merge_distance_threshold,
            "value_merge_borderline_band": s.taxonomy.value_merge_borderline_band,
            "consolidate_values": s.taxonomy.consolidate_values,
            # Summarization
            "skip_summarization": s.summarization.skip,
            "summary_length": s.summarization.summary_length,
            "summary_explanation_length": s.summarization.explanation_length,
            "summary_max_concurrency": s.summarization.max_concurrency,
            # Labeling
            "fallback_category": s.labeling.fallback_category,
            "review_sample_size": s.labeling.review_sample_size,
            # Output
            "max_displayed_documents": s.output.max_displayed_documents,
            "max_docs_per_category_tree": s.output.max_docs_per_category_tree,
            "content_preview_length": s.output.content_preview_length,
            "default_output_dir": s.output.default_output_dir,
            "graph_filename": s.output.graph_filename,
            # Visualization
            "visualization_enabled": s.visualization.enabled,
            "visualization_every_iteration": s.visualization.every_iteration,
            "visualization_dimensions": s.visualization.dimensions,
            "visualization_output_dir": s.visualization.output_dir,
        }
