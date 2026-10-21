"""Unique taxonomy ids, deterministic evidence linking, and validated single-label labeling."""

import asyncio
from types import SimpleNamespace

import numpy as np

from taxonomy_generator.nodes import doc_labeler, evidence_linker
from taxonomy_generator.schemas import LabelOutput
from taxonomy_generator.utils import ensure_unique_ids


# ── Unique ids ─────────────────────────────────────────────────────────────

def test_duplicate_dimension_ids_are_renumbered_and_values_reprefixed():
    clusters = [
        {"id": "37", "name": "A", "values": [{"id": "37.1", "label": "a1"}]},
        {"id": "37", "name": "B", "values": [{"id": "37.1", "label": "b1"}, {"id": "37.1", "label": "b2"}]},
        {"id": "2", "name": "C", "values": []},
    ]
    fixed, changes = ensure_unique_ids(clusters)
    assert [c["id"] for c in fixed] == ["37", "38", "2"]
    assert [v["id"] for v in fixed[1]["values"]] == ["38.1", "38.2"]
    assert all(v["dimension_id"] == "38" for v in fixed[1]["values"])
    assert changes and clusters[1]["id"] == "37"  # input not mutated


def test_unique_ids_leave_a_clean_taxonomy_unchanged():
    clusters = [{"id": "1", "name": "A", "values": [{"id": "1.1", "dimension_id": "1", "label": "a"}]}]
    fixed, changes = ensure_unique_ids(clusters)
    assert fixed == clusters and changes == []


# ── Evidence linking ───────────────────────────────────────────────────────

def test_assign_codes_separates_candidates_from_outcomes_and_respects_threshold():
    values = np.array([[1.0, 0.0], [0.0, 1.0]])           # v0 accepted, v1 outcome
    codes = np.array([[1.0, 0.0], [0.6, 0.8], [0.0, 1.0], [0.2, 0.1]])
    codes = codes / np.linalg.norm(codes, axis=1, keepdims=True)
    out = evidence_linker.assign_codes(
        codes, ["accepted", "rejected", "outcome", "accepted"],
        values, ["accepted", "outcome"], min_similarity=0.5,
    )
    # code 1 is closer to v1, but v1 is an outcome, so the (rejected) candidate code goes to v0.
    assert out == [0, 0, 1, 0]
    assert evidence_linker.assign_codes(codes[:1], ["accepted"], values, ["accepted", "outcome"], 1.01) == [None]


def test_link_evidence_records_stances_and_derives_mixed_status(monkeypatch):
    monkeypatch.setattr(evidence_linker, "load_embeddings_model", lambda name: _FakeEmbeddings())
    clusters = [{"id": "1", "name": "Replication", "values": [
        {"id": "1.1", "label": "Consensus replication", "status": "accepted", "supporting_doc_ids": []}]}]
    codes = [
        {"doc_id": "s01_p01", "label": "Replication via consensus", "rationale": "", "status": "accepted"},
        {"doc_id": "s04_p02", "label": "Replication by consensus rejected", "rationale": "", "status": "rejected"},
    ]
    linked, _ = asyncio.run(evidence_linker.link_evidence(clusters, codes, "fake/model", 0.5))
    value = linked[0]["values"][0]
    assert value["stances"] == {"accepted": ["s01_p01"], "rejected": ["s04_p02"]}
    assert value["status"] == "mixed"


class _FakeEmbeddings:
    """Maps known texts to fixed 2-D directions so assignments are predictable."""

    async def aembed_documents(self, texts):
        return [[1.0, 0.0] if "replication" in t.lower() else [0.0, 1.0] for t in texts]


def test_link_evidence_records_supporting_documents_and_counts(monkeypatch):
    monkeypatch.setattr(evidence_linker, "load_embeddings_model", lambda name: _FakeEmbeddings())
    clusters = [
        {"id": "1", "name": "Replication", "values": [
            {"id": "1.1", "label": "Consensus replication", "status": "accepted", "supporting_doc_ids": ["s01_p01", "ghost"]}]},
        {"id": "2", "name": "Storage", "values": [
            {"id": "2.1", "label": "Object storage", "status": "accepted", "supporting_doc_ids": []}]},
    ]
    codes = [
        {"doc_id": "s01_p01", "label": "Uses replication", "rationale": "", "status": "accepted"},
        {"doc_id": "s02_p03", "label": "Replication via consensus", "rationale": "", "status": "accepted"},
        {"doc_id": "s03_p01", "label": "Stores logs in S3", "rationale": "", "status": "accepted"},
    ]
    linked, stats = asyncio.run(evidence_linker.link_evidence(clusters, codes, "fake/model", 0.5))
    v1, v2 = linked[0]["values"][0], linked[1]["values"][0]
    assert v1["supporting_doc_ids"] == ["s01_p01", "s02_p03"]  # "ghost" is not a real document
    assert v1["evidence_code_count"] == 2 and v2["supporting_doc_ids"] == ["s03_p01"]
    assert linked[0]["evidence"] == {"codes": 2, "documents": 2, "sources": 2}
    assert stats["assigned"] == 3 and stats["documents_with_evidence"] == 3


def test_link_evidence_is_fail_soft(monkeypatch):
    def boom(name):
        raise RuntimeError("no network")
    monkeypatch.setattr(evidence_linker, "load_embeddings_model", boom)
    clusters = [{"id": "1", "name": "A", "values": [{"id": "1.1", "label": "a", "status": "accepted"}]}]
    codes = [{"doc_id": "d1", "label": "x", "rationale": "", "status": "accepted"}]
    linked, stats = asyncio.run(evidence_linker.link_evidence(clusters, codes, "fake/model", 0.3))
    assert linked == clusters and stats["assigned"] == 0


def test_source_of_passage_ids():
    assert evidence_linker.source_of("s03_p02") == "s03"
    assert evidence_linker.source_of("some-uuid") == "some-uuid"


# ── Labeling ───────────────────────────────────────────────────────────────

TAXONOMY = [
    {"id": "4", "name": "Reward objective integrity monitoring", "values": [{"id": "4.1", "label": "Proxy audits"}]},
    {"id": "9", "name": "Drift alert thresholding", "values": []},
]


def _label(category, category_id=None, value_id=None):
    return LabelOutput(reasoning="r", category=category, category_id=category_id, score=0.9, value_id=value_id)


def test_resolve_category_by_id_then_name_then_normalized_name():
    resolve = doc_labeler._resolve_category
    assert resolve(TAXONOMY, _label("anything", "9"), "Other")[0]["id"] == "9"
    assert resolve(TAXONOMY, _label("Drift alert thresholding"), "Other")[0]["id"] == "9"
    assert resolve(TAXONOMY, _label("drift-alert  Thresholding!"), "Other")[0]["id"] == "9"
    assert resolve(TAXONOMY, _label("Other"), "Other") == (None, True)
    assert resolve(TAXONOMY, _label("Reward proxy integrity monitoring"), "Other") == (None, False)


class _ScriptedChain:
    def __init__(self, answers):
        self.answers, self.calls = list(answers), 0

    async def ainvoke(self, inputs):
        self.calls += 1
        return self.answers.pop(0)


def test_invalid_answer_is_retried_then_recorded_as_fallback():
    run = lambda chain: asyncio.run(doc_labeler._label_single_doc(  # noqa: E731
        chain, "text", "{}", asyncio.Semaphore(1), TAXONOMY, "Other"))

    chain = _ScriptedChain([_label("Paraphrased name"), _label("x", "4", "4.1")])
    result, cluster = run(chain)
    assert chain.calls == 2 and cluster["id"] == "4"
    assert doc_labeler._resolve_value_label(cluster, result) == "Proxy audits"

    chain = _ScriptedChain([_label("Nope"), _label("Still nope")])
    result, cluster = run(chain)
    assert chain.calls == 2 and cluster is None
    assert result.category == "Other" and result.score == 0.0 and "not a dimension" in result.reasoning


def test_labeling_uses_selected_taxonomy_when_present():
    full = TAXONOMY + [{"id": "12", "name": "Dropped by selection", "values": []}]
    state = SimpleNamespace(clusters=[full], selected_clusters=[TAXONOMY])
    assert doc_labeler._labeling_taxonomy(state) == TAXONOMY
    assert doc_labeler._labeling_taxonomy(SimpleNamespace(clusters=[full], selected_clusters=[])) == full


def test_placeholder_null_strings_are_treated_as_absent():
    cluster = TAXONOMY[0]
    no_option = LabelOutput(reasoning="r", category=cluster["name"], category_id="null", score=0.8,
                            value_id="null", proposed_value_label="None")
    assert doc_labeler._resolve_category(TAXONOMY, no_option, "Other")[0] is cluster  # falls back to the name
    assert doc_labeler._resolve_value_label(cluster, no_option) is None
    proposal = no_option.model_copy(update={"value_id": " NULL ", "proposed_value_label": "Audit trail"})
    assert doc_labeler._resolve_value_label(cluster, proposal) == "Audit trail"
