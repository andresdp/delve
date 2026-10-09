"""benchmark/focus_variant.py: a decision-focus variant of a saved run (stub model, no LLM)."""

import asyncio
import importlib.util
import json
from pathlib import Path

from taxonomy_generator.schemas import DimensionFocusOutput, SiblingGroup, SiblingMergeOutput, ValueFocus

_spec = importlib.util.spec_from_file_location(
    "focus_variant", Path(__file__).resolve().parents[2] / "benchmark" / "focus_variant.py")
focus_variant = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(focus_variant)


def _value(vid, docs, status="accepted"):
    return {"id": vid, "label": f"v{vid}", "description": "d", "status": status, "dimension_id": vid.split(".")[0],
            "supporting_doc_ids": docs, "evidence_code_count": len(docs)}


def _consolidated():
    return [
        {"id": "1", "name": "Dim A", "description": "qa", "relations": [],
         "values": [_value("1.1", ["s01_p01"]), _value("1.2", ["s02_p01"])]},
        {"id": "2", "name": "Dim B", "description": "qb", "relations": [],
         "values": [_value("2.1", ["s01_p02"]), _value("2.2", ["s01_p03"])]},
        {"id": "3", "name": "Dim C", "description": "qc", "relations": [],
         "values": [_value("3.1", ["s03_p01"]), _value("3.2", ["s04_p01"])]},
    ]


RUN = {"taxonomy_name": "x", "iterations": [{"clusters": []}, {"clusters": _consolidated()}],
       "selected_clusters": _consolidated(), "dropped_dimensions": [], "evaluation": {"overall": 0.6}}


class Stub:
    def __init__(self, replies):
        self.replies, self.schema = replies, None

    def with_structured_output(self, schema):
        bound = Stub(self.replies)
        bound.schema = schema
        return bound

    async def ainvoke(self, messages):
        reply = self.replies[self.schema]
        return reply("\n".join(str(getattr(m, "content", m)) for m in messages)) if callable(reply) else reply


MERGE_AB = SiblingMergeOutput(groups=[SiblingGroup(dimension_ids=["1", "2"], question="q", name="Dim AB",
                                                   description="d", reason="r")])
NO_MOVES = DimensionFocusOutput(values=[])


def test_derive_replaces_selection_and_keeps_other_fields():
    out = asyncio.run(focus_variant.derive(RUN, Stub({SiblingMergeOutput: MERGE_AB}), "u", ["merge"],
                                           min_sources=2, min_candidates=2, variant="merge", model_name="stub"))
    assert [c["name"] for c in out["selected_clusters"]] == ["Dim AB", "Dim C"]
    assert out["evaluation"] == {"overall": 0.6} and out["iterations"] == RUN["iterations"]
    assert out["derived_from"]["variant"] == "merge" and out["derived_from"]["model"] == "stub"
    assert out["decision_focus_log"][0]["pass"] == "merge"
    assert RUN["selected_clusters"][0]["name"] == "Dim A"  # input untouched


def test_dimension_below_minimum_support_after_a_move_is_dropped_with_a_rationale():
    # Dim B's two values both come from source s01, so the recomputed summary has one source and the
    # minimum-support rule drops it with a recorded rationale.
    out = asyncio.run(focus_variant.derive(RUN, Stub({DimensionFocusOutput: NO_MOVES}), "u", ["rehome"],
                                           min_sources=2, min_candidates=2, variant="rehome", model_name="stub"))
    assert [c["id"] for c in out["selected_clusters"]] == ["1", "3"]
    dropped = {d["id"]: d["rationale"] for d in out["dropped_dimensions"]}
    assert "2" in dropped and "1 source" in dropped["2"]


def test_move_that_empties_support_drops_the_source_dimension():
    def reply(text):
        under_review = text.split("Decision point under review", 1)[-1][:200]
        if "Dim A" in under_review:
            return DimensionFocusOutput(values=[ValueFocus(value_id="1.2", action="move", to_dimension_id="3",
                                                           reason="r")])
        return NO_MOVES

    out = asyncio.run(focus_variant.derive(RUN, Stub({DimensionFocusOutput: reply}), "u", ["rehome"],
                                           min_sources=2, min_candidates=2, variant="rehome", model_name="stub"))
    ids = [c["id"] for c in out["selected_clusters"]]
    assert "1" not in ids and "3" in ids  # Dim A keeps one value from one source


def test_outcome_that_leaves_one_candidate_drops_the_dimension_by_the_candidate_rule():
    def reply(text):
        under_review = text.split("Decision point under review", 1)[-1][:200]
        if "Dim C" in under_review:
            return DimensionFocusOutput(values=[ValueFocus(value_id="3.2", action="outcome", to_dimension_id="",
                                                           reason="a goal")])
        return NO_MOVES

    out = asyncio.run(focus_variant.derive(RUN, Stub({DimensionFocusOutput: reply}), "u", ["rehome"],
                                           min_sources=1, min_candidates=2, variant="rehome", model_name="stub"))
    assert "3" not in [c["id"] for c in out["selected_clusters"]]
    dropped = {d["id"]: d["rationale"] for d in out["dropped_dimensions"]}
    assert "3" in dropped and "candidate decision" in dropped["3"]


def test_cli_writes_a_variant_sibling_with_the_original_timestamp(tmp_path):
    run_path = tmp_path / "c2-x_taxonomy_20260101_000000.json"
    run_path.write_text(json.dumps(RUN))
    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  min_dimension_sources: 2\n  min_candidate_decisions: 2\n  use_case: u\n")
    rc = focus_variant.main([str(run_path), "--config", str(cfg), "--variant", "merge-rehome"],
                            model=Stub({SiblingMergeOutput: MERGE_AB, DimensionFocusOutput: NO_MOVES}))
    assert rc == 0
    out = json.loads((tmp_path / "c2-x-merge-rehome_taxonomy_20260101_000000.json").read_text())
    assert [entry["pass"] for entry in out["decision_focus_log"]] == ["merge", "rehome"]


def test_cli_rejects_a_file_that_is_not_a_saved_taxonomy(tmp_path):
    bad = tmp_path / "notes.json"
    bad.write_text("{}")
    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  use_case: u\n")
    assert focus_variant.main([str(bad), "--config", str(cfg), "--variant", "merge"], model=Stub({})) == 2
