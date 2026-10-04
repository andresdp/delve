"""Stage funnel (A10): stage labels, gating, loss stages, outputs — no API calls."""

import asyncio
import json

import numpy as np
import pytest

from taxonomy_generator.evaluation import gt_match, stage_funnel
from taxonomy_generator.evaluation.stage_funnel import (
    ABSENT,
    PRESENT,
    UNJUDGED,
    FunnelSettings,
    Stage,
)

# ---------------------------------------------------------------------- fakes


class RuleJudge:
    """A judge that says 'same' when both items mention one of ``matches`` keywords, else 'different'."""

    def __init__(self, matches):
        self.matches = matches
        self.calls = []

    async def a_generate(self, prompt, schema=None):
        self.calls.append(prompt)
        first = prompt.split("Item 1:", 1)[1].split("\nItem 2:", 1)[0]
        second = prompt.split("Item 2:", 1)[1].split("\n", 1)[0]
        label = "different"
        for key in self.matches:
            if key in first and key in second:
                label = "same"
        return schema(label=label, reason=label), 0.0

    def get_model_name(self):
        return "rule-judge"


def _unit(angle_deg):
    a = np.deg2rad(angle_deg)
    return [float(np.cos(a)), float(np.sin(a)), 0.0]


def embed_by_keyword(table):
    def embed(texts):
        out = []
        for text in texts:
            for key, vec in table.items():
                if key in text:
                    out.append(vec)
                    break
            else:
                out.append(_unit(170))  # far from everything
        return np.asarray(out, dtype=float)
    return embed


def _config(**overrides):
    base = dict(matching_llm="openai/judge-model", generation_llm="openai/generator", embedding="openai/emb",
                lower_threshold=0.0, upper_threshold=0.6, max_candidates=5, include_outcomes=False,
                min_alignment_share=0.25, seed=0, cache_path=None, mode="judge", same_threshold=0.18,
                embedding_one_to_one=True)
    base.update(overrides)
    return gt_match.MatcherConfig(**base)


def _option(oid, name, views=("paper",)):
    return gt_match.Item(id=oid, name=name, description="", parent_ids=["d1"], parent_name="Decision",
                         views=set(views))


def _value(vid, label):
    return gt_match.Item(id=vid, name=label, description="", parent_ids=["1"], parent_name="Dim")


def _code(label):
    return {"doc_id": "s01_p01", "label": label, "rationale": "", "status": "accepted"}


# ---------------------------------------------------------------- stage labels


def test_label_iterations_generate_updates_review_consolidated():
    its = [{"clusters": [], "explanation": "x"} for _ in range(4)]
    its.append({"clusters": [{"values": [{"id": "1.1", "stances": {}}]}], "explanation": "Consolidated 5 values"})
    assert stage_funnel.label_iterations(its) == ["generate", "update_1", "update_2", "review", "consolidated"]


def test_label_iterations_without_consolidation_last_is_review():
    its = [{"clusters": [], "explanation": "x"} for _ in range(3)]
    assert stage_funnel.label_iterations(its) == ["generate", "update_1", "review"]


def test_label_iterations_single_iteration():
    assert stage_funnel.label_iterations([{"clusters": []}]) == ["generate"]


def test_open_code_items_have_no_parent_prefix():
    item = stage_funnel.open_code_items([{"doc_id": "s1", "label": "CUSUM test", "rationale": "detects drift"}])[0]
    assert stage_funnel.item_text(item) == "CUSUM test: detects drift"
    assert "›" not in stage_funnel.item_text(item)


# ---------------------------------------------------------------- gating


def test_open_codes_k_grows_with_stage_size():
    settings = FunnelSettings(k=5, code_fraction=0.02)
    small = Stage("open_codes", [_value(str(i), "x") for i in range(100)])
    large = Stage("open_codes", [_value(str(i), "x") for i in range(1000)])
    assert stage_funnel.stage_k(small, settings) == 5
    assert stage_funnel.stage_k(large, settings) == 20
    assert stage_funnel.stage_k(Stage("update_1", large.items), settings) == 5


def test_candidates_respect_threshold_and_order():
    row = np.array([0.5, 0.1, 0.7, 0.3])
    assert stage_funnel.candidates(row, k=3, upper_threshold=0.6) == [1, 3, 0]
    assert stage_funnel.candidates(row, k=2, upper_threshold=0.2) == [1]


# ---------------------------------------------------------------- tracing


def _run_trace(stages, options, judge, table, settings=None):
    return asyncio.run(stage_funnel.trace_options(stages, options, embed_by_keyword(table), judge, _config(),
                                                  settings or FunnelSettings(k=3)))


def test_option_lost_in_loop_gets_loss_stage_after_last_presence():
    stages = [Stage("open_codes", stage_funnel.open_code_items([_code("CUSUM chart")])),
              Stage("generate", [_value("1.1", "CUSUM chart")]),
              Stage("update_1", [_value("1.1", "Other thing")]),
              Stage("selected", [_value("1.1", "Other thing")])]
    option = _option("cusum", "CUSUM chart")
    traces = _run_trace(stages, [option], RuleJudge(["CUSUM"]), {"CUSUM": _unit(0), "Other": _unit(30)})
    status = traces[0].status
    assert status == {"open_codes": PRESENT, "generate": PRESENT, "update_1": ABSENT, "selected": ABSENT}
    names = [s.name for s in stages]
    assert stage_funnel.loss_stage(status, names) == "update_1"


def test_option_never_coded_is_lost_at_open_codes():
    stages = [Stage("open_codes", stage_funnel.open_code_items([_code("Other thing")])),
              Stage("selected", [_value("1.1", "Other thing")])]
    traces = _run_trace(stages, [_option("cusum", "CUSUM chart")], RuleJudge(["CUSUM"]),
                        {"CUSUM": _unit(0), "Other": _unit(30)})
    assert stage_funnel.loss_stage(traces[0].status, ["open_codes", "selected"]) == "open_codes"


def test_option_matched_in_selected_view_has_no_loss_stage():
    stages = [Stage("open_codes", stage_funnel.open_code_items([_code("CUSUM chart")])),
              Stage("selected", [_value("1.1", "CUSUM chart")])]
    traces = _run_trace(stages, [_option("cusum", "CUSUM chart")], RuleJudge(["CUSUM"]), {"CUSUM": _unit(0)})
    assert stage_funnel.loss_stage(traces[0].status, ["open_codes", "selected"]) is None


def test_option_without_candidates_in_threshold_is_unjudged_not_lost():
    stages = [Stage("open_codes", stage_funnel.open_code_items([_code("Far away")])),
              Stage("selected", [_value("1.1", "CUSUM chart")])]
    judge = RuleJudge(["CUSUM"])
    traces = _run_trace(stages, [_option("cusum", "CUSUM chart")], judge, {"CUSUM": _unit(0), "Far": _unit(120)})
    assert traces[0].status["open_codes"] == UNJUDGED
    assert traces[0].status["selected"] == PRESENT


def test_dropped_then_recovered_is_counted_and_ignored_by_loss_stage():
    names = ["open_codes", "generate", "update_1", "update_2", "selected"]
    status = {"open_codes": PRESENT, "generate": PRESENT, "update_1": ABSENT, "update_2": PRESENT,
              "selected": PRESENT}
    assert stage_funnel.dropped_then_recovered(status, names)
    assert stage_funnel.loss_stage(status, names) is None
    status["selected"] = ABSENT
    assert stage_funnel.loss_stage(status, names) == "selected"
    assert not stage_funnel.dropped_then_recovered({"open_codes": PRESENT, "generate": ABSENT}, names)


def test_cached_verdicts_are_reused_across_stages():
    same_value = _value("1.1", "CUSUM chart")
    stages = [Stage("generate", [same_value]), Stage("update_1", [same_value]), Stage("selected", [same_value])]
    judge = RuleJudge(["CUSUM"])
    _run_trace(stages, [_option("cusum", "CUSUM chart")], judge, {"CUSUM": _unit(0)})
    assert len(judge.calls) == 1


def test_judging_stops_at_first_hit():
    stage = Stage("update_1", [_value("1.1", "CUSUM chart"), _value("1.2", "CUSUM variant"),
                               _value("1.3", "CUSUM other")])
    judge = RuleJudge(["CUSUM"])
    settings = FunnelSettings(k=10)
    traces = _run_trace([stage], [_option("cusum", "CUSUM chart")], judge, {"CUSUM": _unit(0)}, settings)
    assert traces[0].status["update_1"] == PRESENT
    assert len(judge.calls) <= stage_funnel.JUDGE_BATCH


def test_failed_judge_calls_leave_the_stage_unjudged():
    class Failing(RuleJudge):
        async def a_generate(self, prompt, schema=None):
            raise RuntimeError("boom")

    traces = _run_trace([Stage("selected", [_value("1.1", "CUSUM chart")])], [_option("cusum", "CUSUM chart")],
                        Failing(["CUSUM"]), {"CUSUM": _unit(0)})
    assert traces[0].status["selected"] == UNJUDGED


# ---------------------------------------------------------------- summary


def test_summary_reports_selected_agreement_with_official_match():
    names = ["open_codes", "selected"]
    t1 = stage_funnel.OptionTrace(_option("a", "A"), {"open_codes": PRESENT, "selected": PRESENT})
    t2 = stage_funnel.OptionTrace(_option("b", "B"), {"open_codes": PRESENT, "selected": ABSENT})
    t3 = stage_funnel.OptionTrace(_option("c", "C", views=("model",)), {"open_codes": ABSENT, "selected": ABSENT})
    official = stage_funnel.official_hits({"pairs": [{"gt_id": "a", "label": "same"}, {"gt_id": "b", "label": "broader"},
                                                     {"gt_id": "c", "label": "related"}]})
    summary = stage_funnel.summarize([t1, t2, t3], names, ["paper", "model"], official)
    assert summary["paper"]["selected_agreement"] == {"both": 1, "funnel_only": 0, "official_only": 1, "neither": 0}
    assert summary["paper"]["loss_stage"] == {"selected": 1}
    assert summary["model"]["never_present"] == 1


# ---------------------------------------------------------------- command


GT = {"paper": {
    "format_version": 1, "study": "toy", "view": "paper", "provenance": {},
    "decisions": [{"id": "d1", "name": "Drift Test", "question": "", "decision_type": "unspecified",
                   "description": "", "description_source": "", "source": "x"}],
    "options": [{"id": "cusum", "name": "CUSUM chart", "decision_ids": ["d1"], "description": "",
                 "description_source": "", "source": "x"}],
    "forces": [], "decision_forces": [], "impacts": [], "decision_links": [],
}}


def _write_run(tmp_path, with_codes=True):
    run = {"iterations": [
        {"clusters": [{"id": "1", "name": "Dim", "values": [{"id": "1.1", "label": "CUSUM chart", "status": "accepted"}]}],
         "explanation": "x"},
        {"clusters": [{"id": "1", "name": "Dim", "values": [{"id": "1.1", "label": "Other", "status": "accepted"}]}],
         "explanation": "y"}],
        "selected_clusters": [{"id": "1", "name": "Dim", "values": [{"id": "1.1", "label": "Other", "status": "accepted"}]}]}
    tax = tmp_path / "toy_taxonomy_20260101_000000.json"
    tax.write_text(json.dumps(run))
    if with_codes:
        (tmp_path / "toy_open_codes_20260101_000000.json").write_text(json.dumps({"open_codes": [_code("CUSUM chart")]}))
    gt = tmp_path / "gt"
    gt.mkdir()
    (gt / "gt_paper.json").write_text(json.dumps(GT["paper"]))
    return tax, gt


def _settings(tmp_path):
    from taxonomy_generator.settings import load_settings
    cfg = tmp_path / "c.yaml"
    cfg.write_text("models:\n  matching_llm: openai/gpt-4.1-mini\nmatcher:\n  cache_path: null\n")
    return load_settings(str(cfg))


def test_run_funnel_writes_outputs(tmp_path):
    tax, gt = _write_run(tmp_path)
    result = asyncio.run(stage_funnel.run_funnel(
        str(tax), str(gt), _settings(tmp_path), embed=embed_by_keyword({"CUSUM": _unit(0), "Other": _unit(30)}),
        judge_model=RuleJudge(["CUSUM"])))
    assert result["stages"] == ["open_codes", "generate", "review", "selected"]
    assert result["summary"]["paper"]["loss_stage"] == {"review": 1}
    for path in result["paths"].values():
        assert path.exists()
    data = json.loads(result["paths"]["json"].read_text())
    assert data["options"][0]["loss_stage"] == "review"


def test_run_funnel_requires_open_codes(tmp_path):
    tax, gt = _write_run(tmp_path, with_codes=False)
    with pytest.raises(gt_match.MatcherError, match="open codes"):
        asyncio.run(stage_funnel.run_funnel(str(tax), str(gt), _settings(tmp_path),
                                            embed=embed_by_keyword({}), judge_model=RuleJudge([])))
