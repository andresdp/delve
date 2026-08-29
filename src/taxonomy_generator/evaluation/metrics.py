"""GEval criteria for the taxonomy evaluation scoreboard.

One GEval metric per row of the review prompt's criteria table
(``prompts/taxonomy_review.md``), adapted from that table's "what to check"
column into everyday-language judging instructions. All criteria use only
``INPUT`` and ``ACTUAL_OUTPUT`` test-case fields — no reference fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

# Module docstring carries the design rationale; entries below are adapted
# from the Review Criteria table in src/taxonomy_generator/prompts/taxonomy_review.md.


@dataclass(frozen=True)
class Criterion:
    """One judge criterion: a display name plus everyday-language instructions."""

    name: str
    criteria: str
    # Data-grounded criteria require a document sample in the test case's
    # INPUT; structural criteria judge the taxonomy alone (vs the use case).
    needs_documents: bool = False


STRUCTURAL_CRITERIA: List[Criterion] = [
    Criterion(
        name="Orthogonality",
        criteria=(
            "Determine whether every dimension in the taxonomy captures a "
            "fundamentally different type of distinction. If two dimensions "
            "are really just different values on the same underlying axis "
            "(for example 'Bug Reports' and 'Feature Requests' are both "
            "values of 'Issue Type'), the taxonomy fails this criterion."
        ),
    ),
    Criterion(
        name="Clarity",
        criteria=(
            "Determine whether the dimension names and descriptions are "
            "clear enough that a labeler could classify documents accurately "
            "without ambiguity, and whether each description explains what "
            "kind of documents fall along that dimension."
        ),
    ),
    Criterion(
        name="Completeness",
        criteria=(
            "Determine whether the taxonomy captures all major axes of "
            "variation implied by the stated use case, or whether recurring "
            "kinds of distinctions are missing. Judge against the use case "
            "in the input, not against topics the use case excludes."
        ),
    ),
    Criterion(
        name="Use case alignment",
        criteria=(
            "Determine whether every dimension serves the stated use case. "
            "Dimensions that exist in the abstract but do not help achieve "
            "the use case in the input should lower the score."
        ),
    ),
    Criterion(
        name="No catch-alls",
        criteria=(
            "Determine whether the taxonomy contains an 'Other', "
            "'Miscellaneous', or similarly vague catch-all dimension, or "
            "whether every dimension is specific enough that a document "
            "clearly belongs or does not belong."
        ),
    ),
    Criterion(
        name="Axis vs. value",
        criteria=(
            "Determine whether each dimension is truly an axis of variation "
            "rather than a single value dressed up as an axis. A dimension "
            "named 'Bug Reports' might really be one value on an 'Issue "
            "Type' axis that also includes feature requests and questions."
        ),
    ),
]

COVERAGE_CRITERION = Criterion(
    name="Dimensional coverage",
    criteria=(
        "Determine whether every document in the input can be placed along "
        "at least one dimension of the taxonomy. Penalize documents that "
        "fit no dimension's axis of variation, naming the document themes "
        "that are left uncovered."
    ),
    needs_documents=True,
)


def build_metrics(
    model: str | None, threshold: float, include_coverage: bool
) -> List[GEval]:
    """Build the GEval instances for a scoreboard run.

    Args:
        model: Bare OpenAI model name (deepeval built-in integration), or
            ``None`` for GEval's default model.
        threshold: Display-only pass threshold (0-1).
        include_coverage: Whether the coverage criterion is included (the
            caller only includes it when documents are available).

    Returns:
        GEval instances with the criterion attached as ``_criterion`` so the
        runner can map results back to their criterion metadata.
    """
    criteria = list(STRUCTURAL_CRITERIA)
    if include_coverage:
        criteria.append(COVERAGE_CRITERION)

    metrics: List[GEval] = []
    for criterion in criteria:
        metric = GEval(
            name=criterion.name,
            criteria=criterion.criteria,
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
            ],
            threshold=threshold,
            model=model,
            async_mode=True,
        )
        # Stash the criterion metadata so the runner can map metric -> row.
        metric._criterion = criterion  # type: ignore[attr-defined]  # noqa: SLF001
        metrics.append(metric)
    return metrics