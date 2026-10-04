"""Scoreboard runner: taxonomy view (+ optional documents) -> scoreboard dict.

Serializes the taxonomy view with the existing ``format_taxonomy()``, builds
one ``LLMTestCase`` per tier, runs each GEval criterion's ``a_measure``, and
assembles the plain scoreboard dict consumed by the terminal panel, the
saved JSON artifacts, and the report section. Failures degrade to a clearly
marked unavailable scoreboard — they never fail an enclosing pipeline run.
"""

from __future__ import annotations

import json
import logging
import random
from typing import Dict, List, Optional

from deepeval.test_case import LLMTestCase

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation.judge import resolve_judge_model
from taxonomy_generator.evaluation.metrics import (
    DOCUMENT_GROUNDED_CRITERIA,
    build_metrics,
)
logger = logging.getLogger(__name__)


def _doc_content(doc: object) -> str:
    """Extract raw content from a ``Doc`` object or a dict."""
    if isinstance(doc, dict):
        return doc.get("content") or ""
    return getattr(doc, "content", "") or ""


def _doc_id(doc: object) -> str:
    if isinstance(doc, dict):
        return str(doc.get("id") or "")
    return str(getattr(doc, "id", "") or "")


def _passage(doc: object) -> str:
    """A passage for the judge, prefixed with its id so reasons can cite it."""
    doc_id = _doc_id(doc)
    return f"[{doc_id}] {_doc_content(doc)}" if doc_id else _doc_content(doc)


def sample_documents(documents: List[object], n: int, seed: Optional[int] = None) -> List[object]:
    """A seeded sample of ``n`` documents spread across sources.

    Documents are grouped by source (``s03`` for passage ``s03_p02``; a
    document without a passage id is its own source), each group is shuffled,
    and documents are taken round-robin across the shuffled sources. The same
    seed and corpus give the same sample, so scores from different iterations
    of a run (and from standalone re-scoring) are judged on the same passages.
    Taking the first ``n`` documents instead would judge coverage on one or two
    sources only.
    """
    from taxonomy_generator.nodes.evidence_linker import source_of

    docs = list(documents or [])
    if n <= 0 or len(docs) <= n:
        return docs
    rng = random.Random(0 if seed is None else seed)
    groups: Dict[str, List[object]] = {}
    for doc in docs:
        groups.setdefault(source_of(_doc_id(doc)) or str(id(doc)), []).append(doc)
    order = list(groups)
    rng.shuffle(order)
    for key in order:
        rng.shuffle(groups[key])
    sample: List[object] = []
    while len(sample) < n:
        for key in order:
            if groups[key] and len(sample) < n:
                sample.append(groups[key].pop())
    return sample


def format_taxonomy_for_judge(clusters: List[Dict]) -> str:
    """The taxonomy as the judge sees it: structure only.

    Keeps what the criteria judge (dimension id/name/description, typed
    relations, value id/label/description/status) and drops provenance
    fields (supporting_doc_ids, stances, evidence counts, merged_from,
    unsupported values), which only lengthen the input and distract the judge.
    """
    items = []
    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        item = {
            "id": cluster.get("id", ""),
            "name": cluster.get("name", ""),
            "description": cluster.get("description", ""),
        }
        relations = [
            {"target_id": r.get("target_id"), "type": r.get("type")}
            for r in cluster.get("relations") or [] if isinstance(r, dict)
        ]
        if relations:
            item["relations"] = relations
        item["values"] = [
            {k: v.get(k) for k in ("id", "label", "description", "status") if v.get(k) is not None}
            for v in cluster.get("values") or [] if isinstance(v, dict)
        ]
        items.append(item)
    return json.dumps(items, indent=2, ensure_ascii=False)


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
            configuration.evaluation_llm
        )
        threshold = configuration.evaluation_threshold
        taxonomy_json = format_taxonomy_for_judge(clusters)

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
                    _passage(d) for d in docs[: configuration.evaluation_max_documents]
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
                "description": criterion.criteria,
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

        # When documents were absent, every document-grounded criterion is
        # present but not evaluated (R2 visibility) — build_metrics excluded
        # them, so add them back as placeholder rows.
        if not include_coverage:
            for criterion in DOCUMENT_GROUNDED_CRITERIA:
                criteria_rows.append(
                    {
                        "name": criterion.name,
                        "description": criterion.criteria,
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
            "model": configuration.evaluation_llm,
            "unavailable": False,
        }
    except Exception as exc:  # noqa: BLE001 — degrade, never fail the run (R7)
        logger.warning("Taxonomy evaluation unavailable: %s", exc)
        return {
            "criteria": [],
            "overall": None,
            "model": configuration.evaluation_llm,
            "unavailable": True,
            "error": str(exc),
        }