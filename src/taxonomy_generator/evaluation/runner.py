"""Scoreboard runner: taxonomy view (+ optional documents) -> scoreboard dict.

Serializes the taxonomy view with the existing ``format_taxonomy()``, builds
one ``LLMTestCase`` per tier, runs each GEval criterion's ``a_measure``, and
assembles the plain scoreboard dict consumed by the terminal panel, the
saved JSON artifacts, and the report section. Failures degrade to a clearly
marked unavailable scoreboard — they never fail an enclosing pipeline run.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from deepeval.test_case import LLMTestCase

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation.judge import resolve_judge_model
from taxonomy_generator.evaluation.metrics import COVERAGE_CRITERION, build_metrics
from taxonomy_generator.utils import format_taxonomy

logger = logging.getLogger(__name__)


def _doc_content(doc: object) -> str:
    """Extract raw content from a ``Doc`` object or a dict."""
    if isinstance(doc, dict):
        return doc.get("content") or ""
    return getattr(doc, "content", "") or ""


async def run_scoreboard(
    clusters: List[Dict],
    documents: List[object] | None,
    configuration: Configuration,
) -> Dict:
    """Score a taxonomy view against the judge criteria.

    Args:
        clusters: The taxonomy view (list of cluster dicts).
        documents: Optional document sample (``Doc`` objects or dicts). When
            empty, the data-grounded coverage criterion is listed as "not
            evaluated" rather than scored.
        configuration: The run configuration (evaluation settings).

    Returns:
        The scoreboard dict per KTD4: ``{"criteria": [...], "overall": ...,
        "model": ..., "unavailable": False}``, or ``{"unavailable": True,
        "error": ...}`` on judge failure.
    """
    try:
        judge_model = resolve_judge_model(
            configuration.evaluation_judge_model or configuration.model
        )
        threshold = configuration.evaluation_threshold
        taxonomy_json = format_taxonomy(clusters)

        docs = list(documents or [])
        include_coverage = bool(docs)
        metrics = build_metrics(judge_model, threshold, include_coverage)

        # Structural tier: the use case is the input being served.
        # Coverage tier: the sampled document contents are the input.
        structural_case = LLMTestCase(
            input=configuration.use_case,
            actual_output=taxonomy_json,
        )
        coverage_case = (
            LLMTestCase(
                input="\n\n".join(
                    _doc_content(d) for d in docs[: configuration.evaluation_max_documents]
                ),
                actual_output=taxonomy_json,
            )
            if include_coverage
            else None
        )

        criteria_rows: List[Dict] = []
        scores: List[float] = []
        for metric in metrics:
            criterion = metric._criterion  # noqa: SLF001 — attached by build_metrics
            case = coverage_case if criterion.needs_documents else structural_case
            await metric.a_measure(case, _show_indicator=False)
            row: Dict = {
                "name": criterion.name,
                "threshold": threshold,
                "evaluated": True,
            }
            if metric.score is not None:
                row["score"] = float(metric.score)
                row["passed"] = bool(metric.score >= threshold)
                scores.append(float(metric.score))
            else:
                row["score"] = None
                row["passed"] = None
            row["reason"] = metric.reason or ""
            criteria_rows.append(row)
            logger.info(
                "Evaluation criterion '%s': score=%s passed=%s",
                criterion.name, row["score"], row["passed"],
            )

        # When documents were absent the coverage row is present but not
        # evaluated (R2 visibility) — build_metrics excluded it, so add it.
        if not include_coverage:
            criteria_rows.append(
                {
                    "name": COVERAGE_CRITERION.name,
                    "threshold": threshold,
                    "score": None,
                    "passed": None,
                    "reason": "",
                    "evaluated": False,
                }
            )

        overall = sum(scores) / len(scores) if scores else None
        return {
            "criteria": criteria_rows,
            "overall": overall,
            "model": configuration.evaluation_judge_model or configuration.model,
            "unavailable": False,
        }
    except Exception as exc:  # noqa: BLE001 — degrade, never fail the run (R7)
        logger.warning("Taxonomy evaluation unavailable: %s", exc)
        return {
            "criteria": [],
            "overall": None,
            "model": configuration.evaluation_judge_model or configuration.model,
            "unavailable": True,
            "error": str(exc),
        }