"""GEval criteria for the taxonomy evaluation scoreboard.

One GEval metric per row of the review prompt's criteria table
(``prompts/taxonomy_review.md``). All criteria use only ``INPUT`` and
``ACTUAL_OUTPUT`` test-case fields — no reference fields.

Each criterion carries fixed **evaluation steps** rather than letting GEval
generate them from the criterion text. Generated steps are re-derived by an
LLM on every scoreboard, so the criterion's interpretation drifts between
iterations; fixed steps keep scores comparable across iterations and runs.
When steps are given, GEval shows the judge only the steps (not the
criterion text), so the steps carry everything the judge must know:

- what the taxonomy format can express (decision points, candidate decisions
  with a stance, outcomes, relations — no forces), so the judge never
  penalizes the absence of elements the format cannot hold;
- that INPUT is context (the use case, or a passage sample), not a request
  the output must answer;
- that only the named criterion is judged, so one defect does not lower
  every score;
- that the reason names the dimensions/values at fault and the change that
  would fix them — this reason is passed to the next update/review pass as
  actionable feedback (``utils.format_evaluation_summary``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from deepeval.metrics import GEval
from deepeval.models import OpenAIModel
from deepeval.test_case import SingleTurnParams


@dataclass(frozen=True)
class Criterion:
    """One judge criterion: a display name, a summary and fixed judging steps."""

    name: str
    # Short, everyday-language statement of the criterion (shown in reports).
    criteria: str
    # Criterion-specific judging steps (shared context/scope/reason steps are
    # added by ``evaluation_steps``).
    steps: Tuple[str, ...] = field(default_factory=tuple)
    # Data-grounded criteria require a document sample in the test case's
    # INPUT; structural criteria judge the taxonomy alone (vs the use case).
    needs_documents: bool = False


TAXONOMY_FORMAT = (
    "ACTUAL_OUTPUT is a design-space taxonomy in JSON. Each dimension is a decision "
    "point: a topic phrased as one question that requires a choice (id, name, "
    "description). Each value is either a candidate decision, i.e. an alternative "
    "answer to its dimension's question, with status 'accepted' (sources adopted it), "
    "'rejected' (sources considered and declined it) or 'mixed' (sources disagree), or "
    "an outcome (status 'outcome'), i.e. an effect of decisions such as a result, cost "
    "or side effect. Dimensions may have typed relations to other dimensions. The "
    "format has no fields for forces, quality attributes, rationale or evidence: never "
    "penalize their absence."
)

STRUCTURAL_CONTEXT = (
    "INPUT is the use case the taxonomy serves. Treat it as context for judging "
    "relevance, not as a request that ACTUAL_OUTPUT must answer point by point."
)

DOCUMENT_CONTEXT = (
    "INPUT is a sample of corpus passages, each prefixed with its id in square "
    "brackets. Passages that discuss no design decision (introductions, background, "
    "biographies, advertisements) are irrelevant and never count against the taxonomy."
)

SCOPE_STEP = (
    "Judge only the criterion described in these steps. Problems that belong to other "
    "criteria (orthogonality, clarity, completeness, use-case alignment, catch-alls, "
    "axis vs. value, one decision point, stance handling, coverage) must not lower this "
    "score."
)

_REASON_INTRO = (
    "Write the reason as actionable feedback for the person who will revise the "
    "taxonomy: name each dimension or value at fault by id and name, and state the "
    "concrete change that fixes it"
)
_REASON_OUTRO = "List at most five issues, most important first. If there is no shortcoming, say so."

# Structural criteria see no data, so their fixes only reorganize what exists:
# a suggested addition would have to be invented. Additions come from the
# document-grounded criteria, which see the passages that support them.
REASON_STEP = (
    f"{_REASON_INTRO}, using only changes that reorganize existing content (e.g. merge "
    "dimensions 2 and 5, move value 4.2 to dimension 6, split dimension 3 into '<question "
    "A>' and '<question B>' when each part keeps at least two candidate decisions, rename "
    "dimension 1 to '<name>', drop dimension 7). Never ask to add a dimension or value: "
    f"you see no data that could support it. {_REASON_OUTRO}"
)

DOCUMENT_REASON_STEP = (
    f"{_REASON_INTRO}, citing the passage ids that support it (e.g. add value '<label>' "
    "to dimension 2, supported by s03_p02; move value 4.2 to dimension 6). "
    f"{_REASON_OUTRO}"
)


def evaluation_steps(criterion: Criterion) -> List[str]:
    """The full, fixed judging steps for ``criterion`` (context + criterion + scope + reason)."""
    if criterion.needs_documents:
        return [TAXONOMY_FORMAT, DOCUMENT_CONTEXT, *criterion.steps, SCOPE_STEP, DOCUMENT_REASON_STEP]
    return [TAXONOMY_FORMAT, STRUCTURAL_CONTEXT, *criterion.steps, SCOPE_STEP, REASON_STEP]


STRUCTURAL_CRITERIA: List[Criterion] = [
    Criterion(
        name="Orthogonality",
        criteria=(
            "Every dimension is a distinct decision point: no two dimensions ask the "
            "same question, and no dimension's candidate decisions are really options of "
            "another dimension."
        ),
        steps=(
            "Phrase each dimension as the question it asks.",
            "Find pairs of dimensions that ask the same or overlapping questions, or "
            "where one dimension's values would be equally valid answers to another "
            "dimension's question.",
            "Score high when all dimensions ask clearly different questions; lower the "
            "score for each overlapping pair.",
            "Choose fixes that keep one question per dimension. When two dimensions ask "
            "different questions but share values, recommend moving each shared value to "
            "the dimension whose question it answers. Recommend merging two dimensions only "
            "when they ask the same question; never recommend merging dimensions that ask "
            "different questions (e.g. a consistency guarantee and a coordination "
            "mechanism), since that creates a broad topic.",
        ),
    ),
    Criterion(
        name="Clarity",
        criteria=(
            "Dimension names and descriptions make the decision question clear, and value "
            "labels and descriptions make the alternatives distinguishable, so a reader "
            "could tell which dimension and value a passage about a design decision "
            "belongs to."
        ),
        steps=(
            "For each dimension, check that its name and description make clear which "
            "question it asks and what range of alternatives it covers.",
            "For each value, check that its label and description distinguish it from the "
            "other values of the same dimension.",
            "Lower the score for vague, overloaded or jargon-only names, descriptions that "
            "do not match the values, and values that cannot be told apart.",
        ),
    ),
    Criterion(
        name="Completeness",
        criteria=(
            "The taxonomy contains the major decision points implied by the use case, "
            "each with its main candidate decisions."
        ),
        steps=(
            "From the use case, infer the main areas in which decisions must be made.",
            "Check whether each area is represented by at least one decision point with "
            "several candidate decisions.",
            "Lower the score for major areas with no decision point, or decision points "
            "with only one candidate decision. Do not penalize topics the use case "
            "excludes or elements the format cannot express.",
        ),
    ),
    Criterion(
        name="Use case alignment",
        criteria="Every dimension serves the stated use case; none is out of its scope.",
        steps=(
            "For each dimension, decide whether the decision it names falls within the "
            "scope of the use case (its subject, lifecycle phase and kind of decision).",
            "Lower the score for each dimension that is out of scope or only "
            "tangentially related.",
        ),
    ),
    Criterion(
        name="No catch-alls",
        criteria=(
            "No dimension or value is a vague catch-all ('Other', 'Miscellaneous', "
            "'General', 'Other approaches')."
        ),
        steps=(
            "Look for dimensions or values whose name or description is a catch-all "
            "bucket (e.g. 'Other', 'Miscellaneous', 'General considerations', 'Other "
            "approaches', 'Various techniques').",
            "Score high when there is none; lower the score for each catch-all found. "
            "This criterion is only about catch-alls.",
        ),
    ),
    Criterion(
        name="Axis vs. value",
        criteria=(
            "Each dimension is a decision point with alternatives, not a single option "
            "presented as a dimension; each value is an option, not a sub-topic."
        ),
        steps=(
            "Check whether any dimension is really one option of a broader decision "
            "(e.g. a dimension 'Canary Releases' that should be a value of 'Rollout "
            "Strategy').",
            "Check whether any value is really a sub-topic or a question of its own rather "
            "than an answer to its dimension's question.",
            "Lower the score for each such dimension or value.",
        ),
    ),
    Criterion(
        name="One decision point",
        criteria=(
            "Each dimension is a single decision point: all its candidate decisions are "
            "alternative answers to one question, rather than a broad topic bundling "
            "several questions. Where the use case names quality attributes or forces, "
            "dimensions whose choice is driven by recognizable quality attributes or "
            "trade-offs are preferred (quality-attribute grounding)."
        ),
        steps=(
            "For each dimension, read its candidate decisions (values with status "
            "accepted, rejected or mixed) and check that all of them answer one and the "
            "same question. Outcome values are effects of decisions and are not counted "
            "as answers.",
            "Lower the score substantially for each broad topic (e.g. 'Governance', "
            "'Infrastructure Strategy', 'Robustness Mechanisms') whose values answer "
            "different questions, and for each dimension with fewer than two candidate "
            "decisions.",
            "Choose fixes that keep every decision point with at least two candidate "
            "decisions. For a broad topic, recommend a split only when every resulting "
            "dimension keeps at least two candidate decisions; otherwise recommend moving "
            "its odd values to the decision points whose questions they answer. For a "
            "dimension with a single candidate decision, recommend merging it into the "
            "decision point whose question its value answers, or merging sibling "
            "dimensions that answer the same question (e.g. three payment dimensions "
            "with one option each become one payment-integration decision point). Never "
            "recommend inventing alternatives.",
            "Secondary preference (quality-attribute grounding): where the use case names "
            "quality attributes, forces or concerns, prefer dimensions whose choice is "
            "evidently driven by such quality attributes, constraints or trade-offs. "
            "Lower the score slightly for dimensions that are arbitrary topical "
            "groupings with no recognizable trade-off, but never penalize a well-formed "
            "decision point only because no quality attribute is named.",
        ),
    ),
    Criterion(
        name="Rejected-alternative handling",
        criteria=(
            "For each candidate decision, the taxonomy makes clear whether sources adopted "
            "it, rejected it, or disagree (status 'accepted', 'rejected' or 'mixed'); a "
            "rejected alternative is never presented as adopted; each candidate decision "
            "appears once with its stance; outcomes (status 'outcome') are kept apart from "
            "candidate decisions."
        ),
        steps=(
            "Check that every value has one of the statuses 'accepted', 'rejected', "
            "'mixed' (candidate decisions) or 'outcome' (effects of decisions); all four "
            "are valid.",
            "Check that the descriptions agree with the status: a rejected or mixed "
            "candidate decision must not be described as simply adopted.",
            "Check that no candidate decision appears twice in the same dimension under "
            "different statuses, and that outcomes are not phrased as alternatives to "
            "choose.",
            "Lower the score for each violation.",
        ),
    ),
]

COVERAGE_CRITERION = Criterion(
    name="Dimensional coverage",
    criteria=(
        "Every sampled passage that discusses a design decision can be placed under at "
        "least one decision point (dimension) of the taxonomy."
    ),
    steps=(
        "For each passage in INPUT that discusses a design decision, decide whether the "
        "decision can be placed under at least one dimension of ACTUAL_OUTPUT.",
        "Score by the share of decision-bearing passages that can be placed. In the "
        "reason, list the ids of passages that cannot be placed and the decision each "
        "one discusses.",
    ),
    needs_documents=True,
)

CANDIDATE_COVERAGE_CRITERION = Criterion(
    name="Candidate-decision coverage",
    criteria=(
        "The options that the sampled passages adopt or reject are named as values "
        "(candidate decisions) of the right dimension."
    ),
    steps=(
        "For each passage in INPUT that adopts or rejects a specific option for a design "
        "decision, check whether a value of the corresponding dimension of ACTUAL_OUTPUT "
        "names that option.",
        "Score by the share of such options that are named. In the reason, list the "
        "missing options with the passage id and the dimension each one should be added "
        "to.",
    ),
    needs_documents=True,
)

# Criteria requiring a document sample. build_metrics() includes these only
# when documents are available; runner.py re-adds them as "not evaluated"
# placeholder rows otherwise (R2 visibility), so both sides mirror the same
# list rather than hardcoding the pairing independently.
DOCUMENT_GROUNDED_CRITERIA = (COVERAGE_CRITERION, CANDIDATE_COVERAGE_CRITERION)


def build_metrics(
    model: str | None, threshold: float, include_coverage: bool
) -> List[GEval]:
    """Build the GEval instances for a scoreboard run.

    Args:
        model: Bare OpenAI model name (deepeval built-in integration), or
            ``None`` for GEval's default model.
        threshold: Display-only pass threshold (0-1).
        include_coverage: Whether the document-grounded criteria are included
            (the caller only includes them when documents are available).

    Returns:
        GEval instances with the criterion attached as ``_criterion`` so the
        runner can map results back to their criterion metadata.
    """
    criteria = list(STRUCTURAL_CRITERIA)
    if include_coverage:
        criteria.extend(DOCUMENT_GROUNDED_CRITERIA)

    # deepeval's OpenAIModel defaults to temperature=0.0, which newer
    # reasoning-tier models (e.g. gpt-5.x) reject outright ("Only the
    # default (1) value is supported"). temperature=1.0 is valid for both
    # older and newer OpenAI models, so it is used unconditionally here
    # rather than special-casing by model name.
    judge_model = OpenAIModel(model=model, temperature=1.0)

    metrics: List[GEval] = []
    for criterion in criteria:
        metric = GEval(
            name=criterion.name,
            criteria=criterion.criteria,
            evaluation_steps=evaluation_steps(criterion),
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
            ],
            threshold=threshold,
            model=judge_model,
            async_mode=True,
        )
        # Stash the criterion metadata so the runner can map metric -> row.
        metric._criterion = criterion  # type: ignore[attr-defined]  # noqa: SLF001
        metrics.append(metric)
    return metrics
