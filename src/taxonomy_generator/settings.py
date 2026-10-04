"""Load and validate pipeline settings from a YAML configuration file.

This module provides the central settings mechanism for Delve. It reads
``config.yaml`` (or a user-specified path), validates the values, and
exposes them as frozen dataclasses organised by concern.

Only API keys are read from environment variables / ``.env`` — all other
tunable parameters live in the YAML file.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

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
    """The three LLM roles of the project, plus the embedding model.

    - ``generation_llm`` builds the design space: open coding, summaries, taxonomy
      generation/update/review, consolidation, dimension merging and selection,
      document labeling and the report narrative.
    - ``evaluation_llm`` judges it inside the pipeline: the evaluation scoreboard,
      consistency adjudication and the saturation critic.
    - ``matching_llm`` judges value-option pairs in ground-truth matching (``--match-gt``).

    The roles should use different models; the same model may be configured for
    several roles, which is reported as a warning (``shared_llm_warnings``).
    """

    generation_llm: str = "openai/gpt-5.4-nano"
    evaluation_llm: str = "openai/gpt-5.4-mini"
    matching_llm: str = "openai/gpt-4.1-mini"
    embedding: str = "openai/text-embedding-3-small"


LLM_ROLES = ("generation_llm", "evaluation_llm", "matching_llm")


def shared_llm_warnings(models: ModelSettings, roles: Tuple[str, ...] = LLM_ROLES,
                        involving: Optional[str] = None) -> List[str]:
    """Warnings for LLM roles (among ``roles``) configured with the same model.

    ``involving`` keeps only the pairs that include that role (e.g. ``"matching_llm"``).
    """
    warnings = []
    for i, first in enumerate(roles):
        for second in roles[i + 1:]:
            if involving and involving not in (first, second):
                continue
            a, b = getattr(models, first), getattr(models, second)
            if a and b and a.split("/", 1)[-1].strip().lower() == b.split("/", 1)[-1].strip().lower():
                warnings.append(
                    f"models.{first} and models.{second} are the same model ({a}): "
                    f"the {second.split('_')[0]} is not independent of the {first.split('_')[0]}."
                )
    return warnings


@dataclass(frozen=True)
class PipelineSettings:
    """Pipeline execution parameters."""

    max_runs: int = 0
    sample_size: int = 0
    batch_size: int = 200
    random_seed: Optional[int] = None
    # Run mode: "train" (default) progressively builds/updates the taxonomy;
    # "test" freezes the seeded taxonomy's dimensions and only labels new
    # documents (with value growth) against them.
    mode: str = "train"
    # Path to a saved taxonomy JSON used as the run's starting taxonomy.
    # Required for test mode; in train mode it seeds refinement instead of
    # generating from scratch. None = generate from scratch (today's behavior).
    taxonomy_input: Optional[str] = None
    # Which view of taxonomy_input seeds the run: "auto" (selected view in test
    # mode, final iteration in train mode), "selected" or "final".
    taxonomy_input_view: str = "auto"


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
    value_merge_distance_threshold: float = 0.35
    # Distance band above the threshold routed to LLM adjudication instead of
    # auto-merge or auto-reject.
    value_merge_borderline_band: float = 0.40
    # When False, value consolidation is disabled: the consolidate_values node
    # passes the reviewed taxonomy through unchanged (no embeddings, no LLM
    # adjudication), and visualization places all values of a dimension at a
    # unitary distance on the dimension axis.
    consolidate_values: bool = True
    # Let accepted and rejected values merge when they name the same candidate
    # decision (one source adopts it, another rejects it); the merged value keeps
    # both stances as evidence and gets status "mixed". False = values only merge
    # within their exact status.
    merge_value_stances: bool = True
    # Deterministic evidence linking after consolidation: assign every open code
    # to its most similar value (same decision status) and record the supporting
    # documents on that value, instead of relying on ids the LLM copied forward.
    link_evidence: bool = True
    # Minimum cosine similarity (L2-normalized embeddings) for a code to count as
    # evidence for a value. Calibrated for openai/text-embedding-3-small.
    evidence_min_similarity: float = 0.5
    # Remove values no document supports after evidence linking (kept inspectable
    # on their dimension as ``unsupported_values``).
    drop_unsupported_values: bool = True
    # Merge near-duplicate dimensions (same design decision under different
    # names) before value consolidation: automatic below the distance threshold,
    # LLM-judged within the band above it.
    merge_dimensions: bool = False
    dimension_merge_distance_threshold: float = 0.45
    dimension_merge_borderline_band: float = 0.45
    # Drop (with a recorded rationale) dimensions whose evidence comes from fewer
    # than this many sources. 0 disables the rule.
    min_dimension_sources: int = 0
    # Drop (with a recorded rationale) dimensions with fewer than this many
    # candidate decisions (accepted/rejected values; outcomes do not count).
    # 0 disables the rule.
    min_candidate_decisions: int = 0
    # Saturation tolerance: a minibatch also counts as saturated when at least this
    # share of its open codes is covered. 1.0 = strict (every relevant code covered).
    saturation_min_coverage: float = 1.0
    # Minimum share of the corpus's documents that must be open-coded before
    # saturation may end the update loop (0 = saturation alone decides).
    saturation_min_corpus_fraction: float = 0.0
    # How update_taxonomy and review_taxonomy change the taxonomy (EDIT_MODES):
    # "rewrite" re-emits the whole taxonomy (default); "rewrite_restore" also puts
    # back evidence-backed values a rewrite dropped (an ablation control); "tools"
    # edits it through validated coding operations (taxonomy_editor.py).
    edit_mode: str = "rewrite"
    # Tools mode: maximum model turns per update or review.
    edit_max_steps: int = 8


@dataclass(frozen=True)
class FeedbackSettings:
    """Optional external feedback for taxonomy refinement.

    Consumed by ``main.py`` at startup: the resolved text is wrapped in a
    ``UserFeedback`` and passed into the graph via the input state, where it
    flows into the existing ``{feedback}`` prompt slot of update and review.
    """

    # Inline feedback text.
    text: Optional[str] = None
    # Path to a text/markdown file with feedback. Used only when ``text`` is
    # absent (``text`` wins when both are set).
    file: Optional[str] = None


@dataclass(frozen=True)
class SummarizationSettings:
    """Document summarization parameters."""

    skip: bool = False
    summary_length: int = 20
    explanation_length: int = 30
    max_concurrency: int = 5


@dataclass(frozen=True)
class OpenCodingSettings:
    """Open coding parameters."""

    # What the open coder reads per document: "summary" (the summarization
    # output, falling back to content when absent — the original behavior) or
    # "content" (the full document text, so codes stay grounded in the source
    # even when summarization is on).
    input: str = "summary"


OPEN_CODING_INPUTS = ("summary", "content")
EDIT_MODES = ("rewrite", "rewrite_restore", "tools")


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
class EvaluationSettings:
    """Taxonomy evaluation parameters (deepeval GEval-based scoreboard).

    When enabled, runs score the final taxonomy through LLM-as-judge
    criteria and surface a scoreboard (terminal panel, saved JSON, and a
    grounded-theory report section).
    """

    enabled: bool = True
    # Score threshold (0-1) used for display-only pass/fail flags.
    threshold: float = 0.5
    # Embedding-distance cutoff (Euclidean on L2-normalized vectors) below
    # which dimensions from different taxonomies align automatically during
    # consistency comparison.
    consistency_threshold: float = 0.25
    # Distance band above the threshold routed to judge adjudication instead
    # of auto-align or auto-reject.
    consistency_borderline_band: float = 0.08
    # Max documents sampled for the data-grounded coverage criterion.
    max_documents: int = 20
    # Save every scoreboard of a run (taxonomy JSON "evaluation_history") and
    # show the scores across iterations. The loop's feedback uses the scores
    # either way.
    save_history: bool = True
    # Criteria scored and reported but not fed back to update/review. Completeness
    # is judged against the use case alone (the judge sees no data), so in the
    # loop it pushes for use-case topics the corpus may not support.
    feedback_exclude: Tuple[str, ...] = ("Completeness",)
    # Score the loop's drafts every N iterations (1 = every iteration). The
    # draft of the last minibatch and the final view are always scored.
    every_n_iterations: int = 1


@dataclass(frozen=True)
class MatcherSettings:
    """Ground-truth matcher parameters (``--match-gt``).

    Pairs of system values and ground-truth options are proposed by embedding
    distance (cosine distance, 1 - cosine similarity, lower is closer) and, in the
    borderline band, labeled by an LLM judge: the matching LLM
    (``models.matching_llm``), which should be a different model than the generation
    LLM (``models.generation_llm``); a shared model is warned about, not refused
    (``shared_llm_warnings``).
    """

    # Embedding model (provider/model); None uses models.embedding.
    embedding: Optional[str] = None
    # Distance at or below which a pair is labeled "same" without the judge (0 disables:
    # every "same" comes from the judge).
    lower_threshold: float = 0.0
    # Distance above which a pair is labeled "different" without the judge.
    upper_threshold: float = 0.60
    # Pairs in the band reach the judge only when one item is among the other's
    # max_candidates nearest neighbours (bounds the number of judge calls).
    max_candidates: int = 5
    # Include outcome values as system values (sensitivity run).
    include_outcomes: bool = False
    # Minimum share of matched values/options for a dimension-decision alignment.
    min_alignment_share: float = 0.25
    # Seed of the order in which the judge sees the two items of a pair.
    seed: int = 0
    # Judge results cache (keyed by judge model, instructions and pair).
    cache_path: str = ".cache/gt_match_judge.json"
    # "judge": embeddings propose pairs, the judge labels the borderline ones (default).
    # "embeddings": labels from distance alone, no LLM calls (baseline / sensitivity mode).
    mode: str = "judge"
    # Embeddings mode: distance at or below which a pair is "same" (up to upper_threshold:
    # "related"; beyond: "different").
    same_threshold: float = 0.18
    # Embeddings mode: keep only a one-to-one assignment of "same" pairs (others become
    # "related"), so one generic value cannot match many options.
    embedding_one_to_one: bool = True


@dataclass(frozen=True)
class Settings:
    """Top-level settings container."""

    models: ModelSettings = field(default_factory=ModelSettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)
    taxonomy: TaxonomySettings = field(default_factory=TaxonomySettings)
    summarization: SummarizationSettings = field(default_factory=SummarizationSettings)
    open_coding: OpenCodingSettings = field(default_factory=OpenCodingSettings)
    labeling: LabelingSettings = field(default_factory=LabelingSettings)
    feedback: FeedbackSettings = field(default_factory=FeedbackSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    visualization: VisualizationSettings = field(default_factory=VisualizationSettings)
    evaluation: EvaluationSettings = field(default_factory=EvaluationSettings)
    matcher: MatcherSettings = field(default_factory=MatcherSettings)


# ---------------------------------------------------------------------------
# Helpers to build each section from the raw YAML dict
# ---------------------------------------------------------------------------

# Keys renamed in the unified LLM terminology: old location -> models.<role>.
LEGACY_LLM_KEYS = {
    ("models", "model"): "generation_llm",
    ("evaluation", "judge_model"): "evaluation_llm",
    ("matcher", "judge_model"): "matching_llm",
}


def _build_models(raw: dict, full: Optional[dict] = None) -> ModelSettings:
    """Read models.<role>; accept the pre-unification keys with a deprecation warning.

    ``models.model`` -> ``generation_llm``, ``evaluation.judge_model`` -> ``evaluation_llm``,
    ``matcher.judge_model`` -> ``matching_llm``. ``models.fast_llm`` is ignored: its tasks
    now run on ``generation_llm`` (open coding, summaries, labeling, report) and
    ``evaluation_llm`` (saturation critic). A new key wins over its legacy key.
    """
    full = full if full is not None else {"models": raw}
    values = {role: raw.get(role) for role in LLM_ROLES}
    for (section, key), role in LEGACY_LLM_KEYS.items():
        legacy = (full.get(section) or {}).get(key)
        if legacy is None:
            continue
        if values[role] is None:
            values[role] = legacy
            logger.warning("Config key %s.%s is deprecated; use models.%s (read as models.%s = %s).",
                           section, key, role, role, legacy)
        else:
            logger.warning("Config key %s.%s is deprecated and ignored: models.%s is set.", section, key, role)
    if raw.get("fast_llm") is not None:
        logger.warning("Config key models.fast_llm is deprecated and ignored: its tasks run on "
                       "models.generation_llm (and the saturation critic on models.evaluation_llm).")
    return ModelSettings(
        generation_llm=values["generation_llm"] or ModelSettings.generation_llm,
        evaluation_llm=values["evaluation_llm"] or ModelSettings.evaluation_llm,
        matching_llm=values["matching_llm"] or ModelSettings.matching_llm,
        embedding=raw.get("embedding", ModelSettings.embedding),
    )


def _build_pipeline(raw: dict) -> PipelineSettings:
    return PipelineSettings(
        max_runs=raw.get("max_runs", PipelineSettings.max_runs),
        sample_size=raw.get("sample_size", PipelineSettings.sample_size),
        batch_size=raw.get("batch_size", PipelineSettings.batch_size),
        random_seed=raw.get("random_seed", PipelineSettings.random_seed),
        mode=raw.get("mode", PipelineSettings.mode),
        taxonomy_input=raw.get("taxonomy_input", PipelineSettings.taxonomy_input),
        taxonomy_input_view=raw.get("taxonomy_input_view", PipelineSettings.taxonomy_input_view),
    )


def _build_feedback(raw: dict) -> FeedbackSettings:
    return FeedbackSettings(
        text=raw.get("text", FeedbackSettings.text),
        file=raw.get("file", FeedbackSettings.file),
    )


def _build_taxonomy(raw: dict) -> TaxonomySettings:
    edit_mode = raw.get("edit_mode", TaxonomySettings.edit_mode)
    if edit_mode not in EDIT_MODES:
        raise ValueError(f"taxonomy.edit_mode must be one of {EDIT_MODES}, got {edit_mode!r}")
    edit_max_steps = raw.get("edit_max_steps", TaxonomySettings.edit_max_steps)
    if not isinstance(edit_max_steps, int) or edit_max_steps < 1:
        raise ValueError(f"taxonomy.edit_max_steps must be a positive integer, got {edit_max_steps!r}")
    return TaxonomySettings(
        edit_mode=edit_mode,
        edit_max_steps=edit_max_steps,
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
        merge_value_stances=raw.get("merge_value_stances", TaxonomySettings.merge_value_stances),
        link_evidence=raw.get("link_evidence", TaxonomySettings.link_evidence),
        evidence_min_similarity=raw.get("evidence_min_similarity", TaxonomySettings.evidence_min_similarity),
        drop_unsupported_values=raw.get("drop_unsupported_values", TaxonomySettings.drop_unsupported_values),
        merge_dimensions=raw.get("merge_dimensions", TaxonomySettings.merge_dimensions),
        dimension_merge_distance_threshold=raw.get(
            "dimension_merge_distance_threshold", TaxonomySettings.dimension_merge_distance_threshold
        ),
        dimension_merge_borderline_band=raw.get(
            "dimension_merge_borderline_band", TaxonomySettings.dimension_merge_borderline_band
        ),
        min_dimension_sources=raw.get("min_dimension_sources", TaxonomySettings.min_dimension_sources),
        min_candidate_decisions=raw.get("min_candidate_decisions", TaxonomySettings.min_candidate_decisions),
        saturation_min_coverage=raw.get("saturation_min_coverage", TaxonomySettings.saturation_min_coverage),
        saturation_min_corpus_fraction=raw.get(
            "saturation_min_corpus_fraction", TaxonomySettings.saturation_min_corpus_fraction
        ),
    )


def _build_summarization(raw: dict) -> SummarizationSettings:
    return SummarizationSettings(
        skip=raw.get("skip", SummarizationSettings.skip),
        summary_length=raw.get("summary_length", SummarizationSettings.summary_length),
        explanation_length=raw.get("explanation_length", SummarizationSettings.explanation_length),
        max_concurrency=raw.get("max_concurrency", SummarizationSettings.max_concurrency),
    )


def _build_open_coding(raw: dict) -> OpenCodingSettings:
    source = raw.get("input", OpenCodingSettings.input)
    if source not in OPEN_CODING_INPUTS:
        raise ValueError(
            f"open_coding.input must be one of {OPEN_CODING_INPUTS}, got {source!r}"
        )
    return OpenCodingSettings(input=source)


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


def _build_evaluation(raw: dict) -> EvaluationSettings:
    return EvaluationSettings(
        enabled=raw.get("enabled", EvaluationSettings.enabled),
        threshold=raw.get("threshold", EvaluationSettings.threshold),
        consistency_threshold=raw.get("consistency_threshold", EvaluationSettings.consistency_threshold),
        consistency_borderline_band=raw.get(
            "consistency_borderline_band", EvaluationSettings.consistency_borderline_band
        ),
        max_documents=raw.get("max_documents", EvaluationSettings.max_documents),
        save_history=raw.get("save_history", EvaluationSettings.save_history),
        feedback_exclude=tuple(raw.get("feedback_exclude", EvaluationSettings.feedback_exclude) or ()),
        every_n_iterations=raw.get("every_n_iterations", EvaluationSettings.every_n_iterations),
    )


def _build_matcher(raw: dict) -> MatcherSettings:
    return MatcherSettings(
        embedding=raw.get("embedding", MatcherSettings.embedding),
        lower_threshold=raw.get("lower_threshold", MatcherSettings.lower_threshold),
        upper_threshold=raw.get("upper_threshold", MatcherSettings.upper_threshold),
        max_candidates=raw.get("max_candidates", MatcherSettings.max_candidates),
        include_outcomes=raw.get("include_outcomes", MatcherSettings.include_outcomes),
        min_alignment_share=raw.get("min_alignment_share", MatcherSettings.min_alignment_share),
        seed=raw.get("seed", MatcherSettings.seed),
        cache_path=raw.get("cache_path", MatcherSettings.cache_path),
        mode=raw.get("mode", MatcherSettings.mode),
        same_threshold=raw.get("same_threshold", MatcherSettings.same_threshold),
        embedding_one_to_one=raw.get("embedding_one_to_one", MatcherSettings.embedding_one_to_one),
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
        models=_build_models(raw.get("models") or {}, raw),
        pipeline=_build_pipeline(raw.get("pipeline", {})),
        taxonomy=_build_taxonomy(raw.get("taxonomy", {})),
        summarization=_build_summarization(raw.get("summarization", {})),
        open_coding=_build_open_coding(raw.get("open_coding") or {}),
        labeling=_build_labeling(raw.get("labeling", {})),
        feedback=_build_feedback(raw.get("feedback", {})),
        output=_build_output(raw.get("output", {})),
        visualization=_build_visualization(raw.get("visualization", {})),
        evaluation=_build_evaluation(raw.get("evaluation", {})),
        matcher=_build_matcher(raw.get("matcher") or {}),
    )

    logger.debug("Loaded settings: %s", settings)
    return settings