"""evaluation/quality_probe.py: link sampling and summaries (the LLM calls are not exercised here)."""

import asyncio

from taxonomy_generator.evaluation import quality_probe as qp


def _clusters():
    def v(vid, status, docs):
        return {"id": vid, "label": vid, "description": "", "status": status, "supporting_doc_ids": docs}
    return [{"id": "1", "name": "D1", "values": [v("1.1", "accepted", ["a", "b", "c"]), v("1.2", "rejected", ["d"])]},
            {"id": "2", "name": "D2", "values": [v("2.1", "mixed", ["e", "f"]), v("2.2", "outcome", ["g"])]}]


def test_sample_links_is_seeded_stratified_and_without_repeats():
    a = qp.sample_links(_clusters(), n=5, seed=1)
    assert a == qp.sample_links(_clusters(), n=5, seed=1)
    assert len(a) == 5 and len({(x["value_id"], x["passage_id"]) for x in a}) == 5
    statuses = {x["status"] for x in a}
    assert {"rejected", "outcome"} <= statuses


def test_sample_links_passes_unused_quota_on():
    links = qp.sample_links(_clusters(), n=7, seed=2)
    assert len(links) == 7  # every link in the fixture


def test_summarize_audits_rates_candidate_kinds_and_focus():
    audits = [
        {"values": [{"id": "1.1", "status": "accepted"}, {"id": "1.2", "status": "rejected"}],
         "audit": {"single_decision": True, "values": [{"value_id": "1.1", "kind": "option"},
                                                       {"value_id": "1.2", "kind": "fact"}]}},
        {"values": [{"id": "2.1", "status": "mixed"}, {"id": "2.2", "status": "outcome"}],
         "audit": {"single_decision": False, "values": [{"value_id": "2.1", "kind": "option"},
                                                        {"value_id": "2.2", "kind": "effect"}]}},
        {"values": [], "audit": None, "error": "x"},
    ]
    s = qp.summarize_audits(audits)
    assert s["dimensions_audited"] == 2 and s["dimensions_failed"] == 1
    assert s["judge_single_decision_rate"] == 0.5
    assert s["focused_rate"] == 1.0  # no candidate value answers another question
    assert s["candidate_values"] == 3  # outcome values are not candidates
    assert s["candidate_kind_rates"]["option"] == round(2 / 3, 3)
    assert s["kinds_by_status"]["outcome"] == {"effect": 1}


def test_summarize_links_excludes_failures():
    links = [{"status": "accepted", "verdict": "supports"}, {"status": "accepted", "verdict": "unrelated"},
             {"status": "rejected", "verdict": None}]
    s = qp.summarize_links(links)
    assert s["failed"] == 1 and s["overall"]["n"] == 2 and s["overall"]["supports"] == 0.5


class _FakeJudge:
    def __init__(self, result):
        self.result = result

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, prompt):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_check_links_records_missing_passages_and_errors():
    links = [{"passage_id": "a", "dimension": "D", "label": "L", "description": "", "status": "accepted"},
             {"passage_id": "zz", "dimension": "D", "label": "L", "description": "", "status": "accepted"}]
    ok = asyncio.run(qp.check_links(_FakeJudge(qp.LinkVerdict(verdict="supports", reason="r")), links, {"a": "text"}))
    assert ok[0]["verdict"] == "supports" and ok[1]["error"] == "passage not in corpus"
    bad = asyncio.run(qp.check_links(_FakeJudge(RuntimeError("boom")), links[:1], {"a": "text"}))
    assert bad[0]["verdict"] is None and "boom" in bad[0]["error"]


def test_audit_drops_unknown_value_ids():
    dim = {"id": "1", "name": "D", "description": "", "values": [{"id": "1.1", "status": "accepted", "label": "x"}]}
    audit = qp.DimensionAudit(decision_question="q?", single_decision=True,
                              values=[qp.ValueKind(value_id="1.1", kind="option", reason="r"),
                                      qp.ValueKind(value_id="9.9", kind="fact", reason="r")])
    out = asyncio.run(qp.audit_dimensions(_FakeJudge(audit), [dim]))
    assert [v["value_id"] for v in out[0]["audit"]["values"]] == ["1.1"]


def test_focused_rate_ignores_outcomes_but_counts_other_question_candidates():
    audits = [{"values": [{"id": "1", "status": "accepted"}, {"id": "2", "status": "accepted"}, {"id": "3", "status": "outcome"}],
               "audit": {"single_decision": False, "values": [{"value_id": "1", "kind": "option"},
                                                              {"value_id": "2", "kind": "other_question"},
                                                              {"value_id": "3", "kind": "other_question"}]}},
              {"values": [{"id": "4", "status": "accepted"}, {"id": "5", "status": "outcome"}],
               "audit": {"single_decision": False, "values": [{"value_id": "4", "kind": "option"},
                                                              {"value_id": "5", "kind": "effect"}]}}]
    assert qp.summarize_audits(audits)["focused_rate"] == 0.5
