"""Deterministic evidence linking: which passages support each value.

During axial coding the LLM rewrites the whole taxonomy every iteration and is
asked to list each value's ``supporting_doc_ids``. In practice it lists only one
or two ids per value and drops earlier ones when it rewrites a value, so most
documents end up recorded as supporting nothing (77% in one benchmark run),
although every document was open-coded.

This module rebuilds that provenance from the open codes, without an LLM:

1. Embed every value (``<dimension>: <label>. <description>``) and every open
   code (``<label>. <rationale>``) with the configured embedding model.
2. Assign each code to its most similar value **of the same decision status**
   (accepted / rejected / outcome — the rule consolidation already applies),
   falling back to any value only when no value of that status exists.
3. Keep the assignment only when the cosine similarity reaches
   ``evidence_min_similarity``; weaker codes stay unassigned and are counted.
4. Record on each value the documents of its assigned codes, unioned with any
   ids the LLM cited that are real documents, plus evidence counts on each
   value and dimension.

Fail-soft: if embedding fails, the taxonomy is returned unchanged.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Tuple

import numpy as np

from taxonomy_generator.utils import l2_normalize, load_embeddings_model

logger = logging.getLogger(__name__)

_PASSAGE_ID = re.compile(r"^(.+?)_p\d+$")

# A value is either a candidate decision (an alternative answer to its dimension's
# question) or an outcome (an effect of decisions). A candidate decision's stance
# comes from its evidence: sources may accept it, reject it, or disagree ("mixed").
CANDIDATE_STATUSES = ("accepted", "rejected", "mixed")
STANCES = ("accepted", "rejected")


def status_group(status: Optional[str]) -> str:
    """``"outcome"`` for outcomes, ``"candidate"`` for accepted/rejected/mixed values."""
    return "outcome" if status == "outcome" else "candidate"


def status_from_stances(stances: Dict[str, List[str]], fallback: str) -> str:
    """``mixed`` when some sources accept and others reject; else the stance present; else ``fallback``."""
    has_accepted, has_rejected = bool(stances.get("accepted")), bool(stances.get("rejected"))
    if has_accepted and has_rejected:
        return "mixed"
    if has_accepted:
        return "accepted"
    if has_rejected:
        return "rejected"
    return fallback


def initial_stances(value: Dict) -> Dict[str, List[str]]:
    """A candidate value's stances: its recorded ``stances``, else its documents under its own status."""
    if value.get("stances"):
        return {k: list(v) for k, v in value["stances"].items() if k in STANCES}
    status = value.get("status", "accepted")
    if status in STANCES:
        return {status: list(value.get("supporting_doc_ids") or [])}
    return {}


def source_of(doc_id: str) -> str:
    """Source of a document id: ``s03`` for passage ``s03_p02``, else the id itself."""
    match = _PASSAGE_ID.match(doc_id)
    return match.group(1) if match else doc_id


def _value_text(cluster: Dict, value: Dict) -> str:
    return f"{cluster.get('name', '')}: {value.get('label', '')}. {value.get('description', '')}".strip()


def _code_text(code: Dict) -> str:
    return f"{code.get('label', '')}. {code.get('rationale', '')}".strip()


def assign_codes(
    code_vectors: np.ndarray,
    code_statuses: List[str],
    value_vectors: np.ndarray,
    value_statuses: List[str],
    min_similarity: float,
) -> List[Optional[int]]:
    """Index of the value each code supports (``None`` when below the threshold).

    Codes only go to values of the same group: accepted/rejected codes to
    candidate decisions (whatever their stance, since a source may reject what
    another adopted), outcome codes to outcomes. Vectors must be L2-normalized,
    so the dot product is the cosine similarity.
    """
    if len(code_vectors) == 0 or len(value_vectors) == 0:
        return [None] * len(code_vectors)
    sims = code_vectors @ value_vectors.T
    groups = np.array([status_group(s) for s in value_statuses])
    assignments: List[Optional[int]] = []
    for i, status in enumerate(code_statuses):
        mask = groups == status_group(status)
        row = sims[i] if not mask.any() else np.where(mask, sims[i], -np.inf)
        best = int(np.argmax(row))
        assignments.append(best if row[best] >= min_similarity else None)
    return assignments


async def link_evidence(
    clusters: List[Dict],
    open_codes: List[Dict],
    embedding_model: str,
    min_similarity: float,
) -> Tuple[List[Dict], Dict]:
    """Attach deterministic, code-based evidence to every value of ``clusters``.

    Returns the updated clusters (new dicts) and a stats dict:
    ``{"codes", "assigned", "unassigned", "documents", "documents_with_evidence"}``.
    """
    values: List[Tuple[int, int]] = []  # (cluster index, value index)
    for ci, cluster in enumerate(clusters):
        if isinstance(cluster, dict):
            for vi, value in enumerate(cluster.get("values") or []):
                if isinstance(value, dict):
                    values.append((ci, vi))
    codes = [c for c in open_codes or [] if isinstance(c, dict) and c.get("doc_id")]
    known_docs = {str(c["doc_id"]) for c in codes}
    stats = {"codes": len(codes), "assigned": 0, "unassigned": len(codes),
             "documents": len(known_docs), "documents_with_evidence": 0}
    if not values or not codes:
        return clusters, stats

    try:
        embeddings = load_embeddings_model(embedding_model)
        value_texts = [_value_text(clusters[ci], clusters[ci]["values"][vi]) for ci, vi in values]
        code_texts = [_code_text(c) for c in codes]
        vectors = l2_normalize(np.asarray(await embeddings.aembed_documents(value_texts + code_texts), dtype=float))
    except Exception as exc:  # noqa: BLE001 — degrade, don't fail the run
        logger.warning("Evidence linking skipped (embedding failed): %s", exc)
        return clusters, stats

    value_vectors, code_vectors = vectors[: len(values)], vectors[len(values):]
    assignments = assign_codes(
        code_vectors,
        [c.get("status", "accepted") for c in codes],
        value_vectors,
        [clusters[ci]["values"][vi].get("status", "accepted") for ci, vi in values],
        min_similarity,
    )

    evidence: Dict[int, List[Tuple[str, str]]] = {}  # value index -> [(doc id, code status)]
    for code, target in zip(codes, assignments):
        if target is not None:
            evidence.setdefault(target, []).append((str(code["doc_id"]), code.get("status", "accepted")))

    linked = [dict(c) if isinstance(c, dict) else c for c in clusters]
    for ci, cluster in enumerate(linked):
        if isinstance(cluster, dict):
            cluster["values"] = [dict(v) if isinstance(v, dict) else v for v in cluster.get("values") or []]
    for idx, (ci, vi) in enumerate(values):
        value = linked[ci]["values"][vi]
        code_evidence = evidence.get(idx, [])
        code_docs = [doc for doc, _ in code_evidence]
        cited = [str(d) for d in value.get("supporting_doc_ids") or [] if str(d) in known_docs]
        # Stances recorded before linking (from consolidation, or the cited documents
        # under the value's own status), captured before supporting_doc_ids changes.
        prior_stances = initial_stances(value)
        value["supporting_doc_ids"] = sorted(set(cited) | set(code_docs))
        value["evidence_code_count"] = len(code_docs)
        if status_group(value.get("status")) == "candidate":
            # Stance per source: which documents adopt this candidate decision and which
            # reject it. The value's status follows from that evidence.
            stances = {k: set(v) & known_docs for k, v in prior_stances.items()}
            for doc, code_status in code_evidence:
                if code_status in STANCES:
                    stances.setdefault(code_status, set()).add(doc)
            value["stances"] = {k: sorted(v) for k, v in stances.items() if v}
            value["status"] = status_from_stances(value["stances"], value.get("status", "accepted"))
    for cluster in linked:
        if isinstance(cluster, dict):
            docs = {d for v in cluster["values"] if isinstance(v, dict) for d in v.get("supporting_doc_ids", [])}
            cluster["evidence"] = {
                "codes": sum(v.get("evidence_code_count", 0) for v in cluster["values"] if isinstance(v, dict)),
                "documents": len(docs),
                "sources": len({source_of(d) for d in docs}),
            }

    assigned = sum(a is not None for a in assignments)
    stats["linked"] = True
    supported = {d for c in linked if isinstance(c, dict) for v in c["values"] if isinstance(v, dict)
                 for d in v.get("supporting_doc_ids", [])}
    stats.update(assigned=assigned, unassigned=len(codes) - assigned, documents_with_evidence=len(supported))
    return linked, stats


def drop_unsupported_values(clusters: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Remove values that no document supports after evidence linking.

    Such a value has no open code behind it (e.g. a concept the LLM added while
    rewriting the taxonomy), so it is not grounded in the data. Removed values
    stay inspectable on their dimension as ``unsupported_values``; the
    dimension's ``evidence`` summary is unchanged (it only counted supported
    values). Returns the clusters and human-readable notes.
    """
    cleaned, notes = [], []
    for cluster in clusters:
        if not isinstance(cluster, dict):
            cleaned.append(cluster)
            continue
        values = [v for v in cluster.get("values") or [] if isinstance(v, dict)]
        kept = [v for v in values if v.get("supporting_doc_ids")]
        removed = [v for v in values if not v.get("supporting_doc_ids")]
        cluster = dict(cluster)
        if removed:
            cluster["values"] = kept
            cluster["unsupported_values"] = list(cluster.get("unsupported_values") or []) + [
                {"id": v.get("id"), "label": v.get("label", ""), "status": v.get("status")} for v in removed]
            notes.extend(f'[{cluster.get("name", "?")}] "{v.get("label", "")}"' for v in removed)
        cleaned.append(cluster)
    return cleaned, notes
