"""Taxonomy quality probe: value kinds, dimension focus and evidence-link precision.

Diagnostic measurements on a saved run, made by an LLM judge and meant to be
spot-checked by hand (paper plan A11 and the "axis vs. value" problem):

- **Dimension audit** (one call per selected dimension): does the dimension answer
  one design question, and is each value an alternative ``option`` for it, or a
  ``fact``, ``effect``, ``goal``, or an option for a different question
  (``other_question``)? ``outcome`` values are audited too; the pipeline already
  labels them as effects.
- **Evidence-link check** (one call per sampled link): does the linked passage
  support the value (``supports`` / ``partial`` / ``unrelated``)? Links are sampled
  with a fixed seed, stratified by value status so rejected and mixed values are
  over-represented.

The judge's labels are not ground truth: they estimate rates and point to examples.
"""

from __future__ import annotations

import asyncio
import random
from collections import Counter
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence

from pydantic import BaseModel, Field

VALUE_KINDS = ("option", "fact", "effect", "goal", "other_question")
LINK_VERDICTS = ("supports", "partial", "unrelated")
CANDIDATE_STATUSES = ("accepted", "mixed", "rejected")


class ValueKind(BaseModel):
    value_id: str
    kind: Literal["option", "fact", "effect", "goal", "other_question"]
    reason: str = Field(description="One short sentence.")


class DimensionAudit(BaseModel):
    decision_question: str = Field(description="The single design question the dimension answers, as one question.")
    single_decision: bool = Field(description="True if all option values answer that one question.")
    mixed_reason: str = Field(default="", description="If not single_decision: which questions are mixed, briefly.")
    values: List[ValueKind]


class LinkVerdict(BaseModel):
    verdict: Literal["supports", "partial", "unrelated"]
    reason: str = Field(description="One short sentence.")


DIMENSION_PROMPT = """You audit one dimension of a design space mined from software-architecture documents.
A dimension should name ONE architectural design decision (a design question); its values should be the
alternative options for that question (adopted, considered or rejected).

Dimension: {name}
Description: {description}

Values (id | status | label: description):
{values}

1. State the single design question this dimension answers.
2. Say whether all option values answer that one question (single_decision). If the values answer two or
   more different questions, set it false and name them in mixed_reason.
3. Classify every value:
   - option: an alternative answer to the dimension's question (a choice someone could adopt or reject);
   - fact: a property, background fact or description of how something works, not a choice;
   - effect: a consequence or outcome of choices (performance result, risk, cost);
   - goal: a requirement, objective or principle, not a choice;
   - other_question: a genuine choice, but for a different design question than this dimension's.
Return every value id exactly once."""

LINK_PROMPT = """Does this passage support the design-space value below? "Support" means the passage describes,
adopts, considers or rejects this option (or states this effect), not merely mentions related words.

Dimension: {dimension}
Value: {label}: {description} (status: {status})

Passage {passage_id}:
\"\"\"
{passage}
\"\"\"

Answer supports (the passage clearly is evidence for this value), partial (related, but only part of the
value or only indirectly), or unrelated (it is not evidence for this value)."""


def sample_links(clusters: Sequence[Mapping[str, Any]], n: int, seed: int,
                 weights: Optional[Mapping[str, float]] = None) -> List[Dict[str, Any]]:
    """Seeded, status-stratified sample of (value, passage) evidence links, without repeats.

    ``weights`` gives the share of the sample per status (default: accepted 0.4,
    mixed 0.2, rejected 0.2, outcome 0.2); a status with too few links passes its
    remaining quota on to the others.
    """
    weights = dict(weights or {"accepted": 0.4, "mixed": 0.2, "rejected": 0.2, "outcome": 0.2})
    pools: Dict[str, List[Dict[str, Any]]] = {s: [] for s in weights}
    for dim in clusters:
        for v in dim.get("values") or []:
            status = v.get("status", "")
            if status not in pools:
                continue
            for doc in v.get("supporting_doc_ids") or []:
                pools[status].append({"dimension_id": str(dim.get("id")), "dimension": dim.get("name", ""),
                                      "value_id": str(v.get("id")), "label": v.get("label", ""),
                                      "description": v.get("description", ""), "status": status,
                                      "passage_id": str(doc)})
    rng = random.Random(seed)
    for pool in pools.values():
        pool.sort(key=lambda x: (x["value_id"], x["passage_id"]))
        rng.shuffle(pool)
    quota = {s: int(round(n * w)) for s, w in weights.items()}
    picked: List[Dict[str, Any]] = []
    for s in weights:
        picked += pools[s][:quota[s]]
    spare = [x for s in weights for x in pools[s][quota[s]:]]
    rng.shuffle(spare)
    picked += spare[:max(0, n - len(picked))]
    return picked[:n]


def summarize_audits(audits: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Rates over dimension audits.

    A dimension is *focused* when none of its candidate values (accepted, mixed,
    rejected) answers a different design question. The judge's own
    ``single_decision`` flag is kept for reference only: it also counts ``outcome``
    values, which the pipeline keeps on a dimension on purpose, as mixing.
    """
    dims = [a for a in audits if a.get("audit")]
    kinds_by_status: Dict[str, Counter] = {}
    focused = 0
    for a in dims:
        status_of = {str(v["id"]): v.get("status", "") for v in a["values"]}
        other = 0
        for vk in a["audit"]["values"]:
            status = status_of.get(vk["value_id"], "?")
            kinds_by_status.setdefault(status, Counter())[vk["kind"]] += 1
            other += status in CANDIDATE_STATUSES and vk["kind"] == "other_question"
        focused += other == 0
    candidates = Counter()
    for s in CANDIDATE_STATUSES:
        candidates.update(kinds_by_status.get(s, Counter()))
    total = sum(candidates.values())
    return {
        "dimensions_audited": len(dims),
        "dimensions_failed": len(audits) - len(dims),
        "focused_rate": round(focused / len(dims), 3) if dims else None,
        "judge_single_decision_rate": round(sum(a["audit"]["single_decision"] for a in dims) / len(dims), 3) if dims else None,
        "candidate_values": total,
        "candidate_kind_rates": {k: round(candidates[k] / total, 3) for k in VALUE_KINDS} if total else {},
        "kinds_by_status": {s: dict(c) for s, c in kinds_by_status.items()},
    }


def summarize_links(links: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Verdict rates overall and per value status (failed calls excluded)."""
    judged = [x for x in links if x.get("verdict") in LINK_VERDICTS]
    def rates(items):
        c = Counter(x["verdict"] for x in items)
        return {"n": len(items), **{v: round(c[v] / len(items), 3) for v in LINK_VERDICTS}} if items else {"n": 0}
    statuses = sorted({x["status"] for x in judged})
    return {"overall": rates(judged), "failed": len(links) - len(judged),
            "by_status": {s: rates([x for x in judged if x["status"] == s]) for s in statuses}}


async def audit_dimensions(model: Any, clusters: Sequence[Mapping[str, Any]], concurrency: int = 6) -> List[Dict[str, Any]]:
    """Run the dimension audit with a LangChain chat model; failures are kept with an error."""
    judge = model.with_structured_output(DimensionAudit)
    sem = asyncio.Semaphore(concurrency)

    async def one(dim):
        values = "\n".join(f"{v.get('id')} | {v.get('status')} | {v.get('label')}: {v.get('description', '')}"
                           for v in dim.get("values") or [])
        prompt = DIMENSION_PROMPT.format(name=dim.get("name", ""), description=dim.get("description", ""), values=values)
        async with sem:
            try:
                result = await judge.ainvoke(prompt)
                audit = result.model_dump()
                ids = {str(v.get("id")) for v in dim.get("values") or []}
                audit["values"] = [v for v in audit["values"] if v["value_id"] in ids]
                return {"id": str(dim.get("id")), "name": dim.get("name", ""), "values": dim.get("values") or [],
                        "audit": audit}
            except Exception as exc:  # noqa: BLE001 - recorded, not fatal
                return {"id": str(dim.get("id")), "name": dim.get("name", ""), "values": dim.get("values") or [],
                        "audit": None, "error": str(exc)[:300]}

    return await asyncio.gather(*(one(d) for d in clusters))


async def check_links(model: Any, links: Sequence[Mapping[str, Any]], passages: Mapping[str, str],
                      concurrency: int = 8) -> List[Dict[str, Any]]:
    """Judge each sampled link against its passage text; failures are kept with an error."""
    judge = model.with_structured_output(LinkVerdict)
    sem = asyncio.Semaphore(concurrency)

    async def one(link):
        text = passages.get(link["passage_id"])
        if text is None:
            return {**link, "verdict": None, "reason": "", "error": "passage not in corpus"}
        prompt = LINK_PROMPT.format(passage=text, **link)
        async with sem:
            try:
                result = await judge.ainvoke(prompt)
                return {**link, "verdict": result.verdict, "reason": result.reason}
            except Exception as exc:  # noqa: BLE001
                return {**link, "verdict": None, "reason": "", "error": str(exc)[:300]}

    return await asyncio.gather(*(one(x) for x in links))
