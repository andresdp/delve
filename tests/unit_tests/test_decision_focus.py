"""Decision-focus passes (merge siblings, rehome values) with a stub model."""

import asyncio

from taxonomy_generator.nodes import decision_focus as df
from taxonomy_generator.schemas import (
    DimensionFocusOutput,
    SiblingGroup,
    SiblingMergeOutput,
    ValueFocus,
)


def _taxonomy():
    def value(vid, label, status, docs, codes=1):
        return {"id": vid, "label": label, "description": f"{label} desc", "status": status,
                "dimension_id": vid.split(".")[0], "supporting_doc_ids": docs, "evidence_code_count": codes}

    return [
        {"id": "1", "name": "Drift Test", "description": "Which test detects drift?",
         "relations": [{"target_id": "2", "type": "consequence", "rationale": "r"}],
         "evidence": {"codes": 0, "documents": 0, "sources": 0},
         "values": [value("1.1", "KS test", "accepted", ["s01_p01"]),
                    value("1.2", "Page-Hinkley", "rejected", ["s02_p01"]),
                    value("1.3", "Alert on Slack", "accepted", ["s03_p02"])]},
        {"id": "2", "name": "Drift Window", "description": "Which window does the drift test use?",
         "relations": [], "evidence": {"codes": 0, "documents": 0, "sources": 0},
         "values": [value("2.1", "Sliding window", "accepted", ["s01_p02"]),
                    value("2.2", "Fixed window", "rejected", ["s02_p02"])]},
        {"id": "3", "name": "Response Action", "description": "How does the system respond to drift?",
         "relations": [{"target_id": "2", "type": "constrains", "rationale": "r"}],
         "evidence": {"codes": 0, "documents": 0, "sources": 0},
         "values": [value("3.1", "Retrain", "accepted", ["s03_p01"]),
                    value("3.2", "Roll back", "accepted", ["s04_p01"]),
                    value("3.3", "Reliable monitoring", "accepted", ["s04_p02"])]},
    ]


class StubModel:
    """Stands in for a chat model: returns a fixed reply per schema (or per dimension id)."""

    def __init__(self, replies):
        self.replies = replies
        self.prompts = []
        self.schema = None

    def with_structured_output(self, schema):
        bound = StubModel(self.replies)
        bound.prompts, bound.schema = self.prompts, schema
        return bound

    async def ainvoke(self, messages):
        text = "\n".join(str(getattr(m, "content", m)) for m in messages)
        self.prompts.append(text)
        reply = self.replies.get(self.schema)
        if callable(reply):
            reply = reply(text)
        if isinstance(reply, Exception):
            raise reply
        return reply


def _dim(clusters, name):
    return next(c for c in clusters if c["name"] == name)


def run(coro):
    return asyncio.run(coro)


def test_merge_joins_a_sibling_group_and_redirects_relations():
    model = StubModel({SiblingMergeOutput: SiblingMergeOutput(groups=[SiblingGroup(
        dimension_ids=["1", "2"], question="How is drift detected?", name="Drift Detection",
        description="How is drift detected, and over which window?", reason="window is part of the test")])})
    clusters, log = run(df.merge_siblings(_taxonomy(), model, "Monitor ML systems."))
    assert [c["name"] for c in clusters] == ["Drift Detection", "Response Action"]
    merged = _dim(clusters, "Drift Detection")
    assert {v["label"] for v in merged["values"]} == {"KS test", "Page-Hinkley", "Alert on Slack",
                                                      "Sliding window", "Fixed window"}
    assert _dim(clusters, "Response Action")["relations"][0]["target_id"] == merged["id"]
    assert len(log["applied"]) == 1 and not log["rejected"]


def test_merge_with_unknown_id_or_duplicate_name_is_rejected_and_logged():
    model = StubModel({SiblingMergeOutput: SiblingMergeOutput(groups=[
        SiblingGroup(dimension_ids=["1", "9"], question="q", name="X", description="d", reason="r"),
        SiblingGroup(dimension_ids=["1", "2"], question="q", name="Response Action", description="d", reason="r"),
    ])})
    clusters, log = run(df.merge_siblings(_taxonomy(), model, "Monitor ML systems."))
    assert [c["name"] for c in clusters] == ["Drift Test", "Drift Window", "Response Action"]
    assert len(log["rejected"]) == 2 and not log["applied"]


def test_rehome_moves_a_value_and_turns_a_goal_into_an_outcome():
    def reply(text):
        if "Drift Test" in text.split("Decision point under review", 1)[-1][:200]:
            return DimensionFocusOutput(values=[
                ValueFocus(value_id="1.3", action="move", to_dimension_id="3", reason="it answers the response"),
                ValueFocus(value_id="1.1", action="keep", to_dimension_id="", reason="fits")])
        if "Response Action" in text.split("Decision point under review", 1)[-1][:200]:
            return DimensionFocusOutput(values=[
                ValueFocus(value_id="3.3", action="outcome", to_dimension_id="", reason="a goal, not a choice")])
        return DimensionFocusOutput(values=[])

    model = StubModel({DimensionFocusOutput: reply})
    clusters, log = run(df.rehome_values(_taxonomy(), model, "Monitor ML systems."))
    response = _dim(clusters, "Response Action")
    assert "Alert on Slack" in {v["label"] for v in response["values"]}
    assert "Alert on Slack" not in {v["label"] for v in _dim(clusters, "Drift Test")["values"]}
    assert next(v for v in response["values"] if v["label"] == "Reliable monitoring")["status"] == "outcome"
    assert len(log["applied"]) == 2


def test_rehome_move_to_unknown_dimension_or_foreign_value_is_rejected():
    def reply(text):
        return DimensionFocusOutput(values=[
            ValueFocus(value_id="1.1", action="move", to_dimension_id="9", reason="r"),
            ValueFocus(value_id="3.1", action="outcome", to_dimension_id="", reason="not in this dimension")])

    model = StubModel({DimensionFocusOutput: lambda text: reply(text) if "Drift Test" in
                       text.split("Decision point under review", 1)[-1][:200] else DimensionFocusOutput(values=[])})
    clusters, log = run(df.rehome_values(_taxonomy(), model, "Monitor ML systems."))
    assert {v["label"] for v in _dim(clusters, "Drift Test")["values"]} == {"KS test", "Page-Hinkley", "Alert on Slack"}
    assert _dim(clusters, "Response Action")["values"][0]["status"] == "accepted"
    assert len(log["rejected"]) == 2 and not log["applied"]


def test_failed_call_for_one_dimension_leaves_it_unchanged_and_others_processed():
    def reply(text):
        under_review = text.split("Decision point under review", 1)[-1][:200]
        if "Drift Test" in under_review:
            return RuntimeError("model down")
        if "Response Action" in under_review:
            return DimensionFocusOutput(values=[ValueFocus(value_id="3.3", action="outcome", to_dimension_id="",
                                                           reason="goal")])
        return DimensionFocusOutput(values=[])

    model = StubModel({DimensionFocusOutput: reply})
    clusters, log = run(df.rehome_values(_taxonomy(), model, "Monitor ML systems."))
    assert len(_dim(clusters, "Drift Test")["values"]) == 3
    assert next(v for v in _dim(clusters, "Response Action")["values"] if v["id"] == "3.3")["status"] == "outcome"
    assert len(log["failed_calls"]) == 1


def test_evidence_summaries_are_recomputed_from_values():
    clusters = df.recompute_evidence(_taxonomy())
    drift = _dim(clusters, "Drift Test")
    assert drift["evidence"] == {"codes": 3, "documents": 3, "sources": 3}
    assert _dim(clusters, "Drift Window")["evidence"] == {"codes": 2, "documents": 2, "sources": 2}


def test_apply_passes_runs_merge_then_rehome_and_recomputes_evidence():
    replies = {
        SiblingMergeOutput: SiblingMergeOutput(groups=[SiblingGroup(
            dimension_ids=["1", "2"], question="q", name="Drift Detection", description="d", reason="r")]),
        DimensionFocusOutput: DimensionFocusOutput(values=[]),
    }
    clusters, log = run(df.apply_passes(_taxonomy(), StubModel(replies), "Monitor ML systems.",
                                        ["merge", "rehome"]))
    assert _dim(clusters, "Drift Detection")["evidence"] == {"codes": 5, "documents": 5, "sources": 3}
    assert [entry["pass"] for entry in log] == ["merge", "rehome"]


def test_prompts_carry_the_use_case_and_taxonomy_and_no_ground_truth():
    model = StubModel({SiblingMergeOutput: SiblingMergeOutput(groups=[]),
                       DimensionFocusOutput: DimensionFocusOutput(values=[])})
    run(df.apply_passes(_taxonomy(), model, "Monitor ML systems.", ["merge", "rehome"]))
    assert model.prompts and all("Monitor ML systems." in p for p in model.prompts)
    assert all("Drift Window" in p for p in model.prompts)
    assert not any("ground truth" in p.lower() or "expert" in p.lower() for p in model.prompts)


def test_unknown_pass_name_is_an_error():
    try:
        run(df.apply_passes(_taxonomy(), StubModel({}), "u", ["split"]))
    except ValueError as exc:
        assert "split" in str(exc)
    else:
        raise AssertionError("expected ValueError")
