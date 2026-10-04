"""Dimension merging, the minimum-support rule, and tolerant saturation."""

import asyncio
from types import SimpleNamespace

from langchain_core.runnables import RunnableLambda

from taxonomy_generator.nodes import dimension_merger
from taxonomy_generator.nodes.dimension_selector import split_by_support
from taxonomy_generator.nodes.saturation_checker import saturation_coverage
from taxonomy_generator.schemas import DimensionMergeOutput


def _dim(i, name, n_values=1, relations=()):
    return {"id": str(i), "name": name, "description": name,
            "values": [{"id": f"{i}.{k}", "label": f"{name} option {k}"} for k in range(1, n_values + 1)],
            "relations": [dict(r) for r in relations]}


# ── Merge groups (pure) ────────────────────────────────────────────────────

def test_merge_groups_keeps_richest_member_and_redirects_relations():
    dims = [
        _dim(1, "RLHF feedback loop", 1, [{"target_id": "3", "type": "enables"}]),
        _dim(2, "RLHF reward-model loop", 3, [{"target_id": "1", "type": "constrains"}]),
        _dim(3, "Alerting", 1, [{"target_id": "1", "type": "complements"}, {"target_id": "2", "type": "complements"}]),
    ]
    merged, notes = dimension_merger.merge_groups(dims, [[0, 1], [2]])
    assert [d["name"] for d in merged] == ["RLHF reward-model loop", "Alerting"]
    rlhf, alerting = merged
    assert len(rlhf["values"]) == 4                      # every member's values are kept
    assert rlhf["merged_from"] == [{"id": "1", "name": "RLHF feedback loop"}]
    assert rlhf["relations"] == [{"target_id": "3", "type": "enables"}]          # self-relation dropped
    assert alerting["relations"] == [{"target_id": "2", "type": "complements"}]  # 1 -> 2, deduplicated
    assert notes and "RLHF feedback loop" in notes[0]


# ── merge_dimensions with fake embeddings and judge ───────────────────────

class _FakeEmbeddings:
    VECTORS = {"A": [1.0, 0.0, 0.0], "B": [0.8, 0.6, 0.0], "C": [0.0, 0.0, 1.0]}

    async def aembed_documents(self, texts):
        return [self.VECTORS[t[0]] for t in texts]


class _FakeChain:
    """Stands in for ``load_chat_model(...)``: its structured output is a Runnable judge."""

    def __init__(self, verdict):
        self.verdict, self.calls = verdict, 0

    def with_structured_output(self, schema):
        async def judge(_prompt_value):
            self.calls += 1
            return DimensionMergeOutput(same_decision=self.verdict, rationale="test")
        return RunnableLambda(judge)


def _config(**kw):
    base = dict(embedding="fake/e", generation_llm="fake/m", use_case="u", summary_max_concurrency=2,
                dimension_merge_distance_threshold=0.1, dimension_merge_borderline_band=0.6)
    return SimpleNamespace(**{**base, **kw})


def _run_merge(monkeypatch, verdict):
    chain = _FakeChain(verdict)
    monkeypatch.setattr(dimension_merger, "load_embeddings_model", lambda name: _FakeEmbeddings())
    monkeypatch.setattr(dimension_merger, "load_chat_model", lambda name: chain)
    dims = [_dim(1, "A decision"), _dim(2, "B decision", 2), _dim(3, "C decision")]
    merged, notes = asyncio.run(dimension_merger.merge_dimensions(dims, _config()))
    return merged, notes, chain


def test_borderline_pair_merges_only_when_the_judge_agrees(monkeypatch):
    # A-B distance ~0.63 is inside the band (0.1, 0.7]; C is far from both.
    merged, notes, chain = _run_merge(monkeypatch, verdict=True)
    assert chain.calls == 1 and [d["name"] for d in merged] == ["B decision", "C decision"]

    merged, notes, chain = _run_merge(monkeypatch, verdict=False)
    assert chain.calls == 1 and len(merged) == 3 and notes == []


def test_merge_dimensions_is_fail_soft(monkeypatch):
    def boom(name):
        raise RuntimeError("no network")
    monkeypatch.setattr(dimension_merger, "load_embeddings_model", boom)
    dims = [_dim(1, "A"), _dim(2, "B")]
    assert asyncio.run(dimension_merger.merge_dimensions(dims, _config())) == (dims, [])


# ── Minimum support ────────────────────────────────────────────────────────

def _with_sources(i, n):
    return {"id": str(i), "name": f"D{i}", "evidence": {"codes": n, "documents": n, "sources": n}}


def test_dimensions_below_min_sources_are_dropped_with_rationale():
    kept, dropped = split_by_support([_with_sources(1, 3), _with_sources(2, 1), _with_sources(3, 2)], 2)
    assert [c["id"] for c in kept] == ["1", "3"]
    assert dropped[0]["id"] == "2" and "1 source" in dropped[0]["rationale"]


def test_min_sources_rule_is_inert_without_evidence_or_when_it_would_drop_everything():
    plain = [{"id": "1", "name": "D1"}, {"id": "2", "name": "D2"}]
    assert split_by_support(plain, 2) == (plain, [])
    weak = [_with_sources(1, 1), _with_sources(2, 1)]
    assert split_by_support(weak, 2) == (weak, [])
    assert split_by_support(weak, 0) == (weak, [])


# ── Saturation coverage ────────────────────────────────────────────────────

def test_saturation_coverage():
    assert saturation_coverage(100, 8) == 0.92
    assert saturation_coverage(0, 0) == 1.0
    assert saturation_coverage(5, 9) == 0.0


# ── Candidate decisions and unsupported values ─────────────────────────────

from taxonomy_generator.nodes.dimension_selector import split_by_candidates  # noqa: E402
from taxonomy_generator.nodes.evidence_linker import drop_unsupported_values  # noqa: E402


def _with_statuses(i, *statuses):
    return {"id": str(i), "name": f"D{i}",
            "values": [{"id": f"{i}.{k}", "label": f"v{k}", "status": s} for k, s in enumerate(statuses, 1)]}


def test_dimensions_without_two_candidate_decisions_are_dropped():
    dims = [_with_statuses(1, "accepted", "rejected", "outcome"),
            _with_statuses(2, "outcome", "outcome", "outcome"),
            _with_statuses(3, "accepted", "outcome")]
    kept, dropped = split_by_candidates(dims, 2)
    assert [c["id"] for c in kept] == ["1"]
    assert [d["id"] for d in dropped] == ["2", "3"] and "Not a decision point" in dropped[0]["rationale"]
    assert split_by_candidates(dims, 0) == (dims, [])
    only_weak = [dims[1], dims[2]]
    assert split_by_candidates(only_weak, 2) == (only_weak, [])  # never drops everything


def test_values_without_evidence_are_removed_but_kept_inspectable():
    clusters = [{"id": "1", "name": "D1", "values": [
        {"id": "1.1", "label": "supported", "status": "accepted", "supporting_doc_ids": ["d1"]},
        {"id": "1.2", "label": "orphan", "status": "accepted", "supporting_doc_ids": []}]}]
    cleaned, notes = drop_unsupported_values(clusters)
    assert [v["label"] for v in cleaned[0]["values"]] == ["supported"]
    assert cleaned[0]["unsupported_values"] == [{"id": "1.2", "label": "orphan", "status": "accepted"}]
    assert notes == ['[D1] "orphan"'] and len(clusters[0]["values"]) == 2  # input not mutated
