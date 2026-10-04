"""Ground-truth matcher, part 1 (adapter, candidates, graded judge) — no API calls."""

import asyncio
import json

import numpy as np
import pytest

from taxonomy_generator.evaluation import gt_match
from taxonomy_generator.settings import load_settings

# ---------------------------------------------------------------------- fakes

class FakeJudgeModel:
    """Stands in for deepeval's OpenAIModel: returns scripted verdicts, counts calls."""

    def __init__(self, labels):
        self.labels = list(labels)
        self.calls = []

    async def a_generate(self, prompt, schema=None):
        self.calls.append(prompt)
        label = self.labels.pop(0) if self.labels else "different"
        return schema(label=label, reason=f"because {label}"), 0.0

    def get_model_name(self):
        return "fake-judge"


def fake_embedder(table):
    """Embed each text to the vector of the first table key it contains."""
    def embed(texts):
        out = []
        for text in texts:
            for key, vec in table.items():
                if key in text:
                    out.append(vec)
                    break
            else:
                raise AssertionError(f"no fake vector for {text!r}")
        return np.asarray(out, dtype=float)
    return embed


def _unit(angle_deg):
    a = np.deg2rad(angle_deg)
    return [float(np.cos(a)), float(np.sin(a)), 0.0]


def _config(**overrides):
    base = dict(matching_llm="openai/judge-model", generation_llm="openai/generator", embedding="openai/emb",
                lower_threshold=0.02, upper_threshold=0.5, max_candidates=5, include_outcomes=False,
                min_alignment_share=0.25, seed=0, cache_path=None, mode="judge", same_threshold=0.18,
                embedding_one_to_one=True)
    base.update(overrides)
    return gt_match.MatcherConfig(**base)


CLUSTERS = [
    {"id": "1", "name": "DriftTest", "description": "Which test detects drift?", "values": [
        {"id": "1.1", "label": "CUSUM chart", "description": "cumulative sums", "status": "accepted"},
        {"id": "1.2", "label": "Mean shift test", "description": "compare means", "status": "rejected"},
        {"id": "1.3", "label": "Faster alerts", "description": "an effect", "status": "outcome"},
    ]},
]
GT = {"paper": {
    "format_version": 1, "study": "toy", "view": "paper", "provenance": {},
    "decisions": [{"id": "add4", "name": "Reward Degradation Test", "question": "", "decision_type": "unspecified",
                   "description": "", "description_source": "", "source": "x"}],
    "options": [
        {"id": "cusum", "name": "CUSUMSequentialTest", "decision_ids": ["add4"], "description": "Cumulative sums",
         "description_source": "model", "source": "x"},
        {"id": "hotelling", "name": "Hotelling Test", "decision_ids": ["add4"], "description": "Multivariate",
         "description_source": "model", "source": "x"},
        {"id": "orphan", "name": "Orphan", "decision_ids": [], "unattached": True, "description": "",
         "description_source": "", "source": "x"},
    ],
    "forces": [], "decision_forces": [], "impacts": [], "decision_links": [],
}}
# Cosine distance = 1 - cos(angle): 3 deg ~0.001, 25 deg ~0.094, 27 deg ~0.109, 55 deg ~0.426.
VECTORS = {
    "CUSUM chart": _unit(0), "CUSUM Sequential Test": _unit(3),   # same
    "Mean shift test": _unit(30),                                  # 27 deg from CUSUM: band
    "Hotelling Test": _unit(55),                                   # 25 deg from Mean shift: band; 55 from CUSUM chart
    "Faster alerts": _unit(170),
}


def _run(config, judge_labels=(), clusters=CLUSTERS, cache=None):
    judge = FakeJudgeModel(judge_labels)
    system = gt_match.system_values(clusters, include_outcomes=config.include_outcomes)
    options = gt_match.ground_truth_options(GT)
    pairs = asyncio.run(gt_match.label_pairs(system, options, fake_embedder(VECTORS), judge, config, cache=cache))
    return pairs, judge


def _pair(pairs, sys_id, gt_id):
    return next(p for p in pairs if p["system_id"] == sys_id and p["gt_id"] == gt_id)


# ---------------------------------------------------------------------- tests

def test_pair_below_the_lower_threshold_is_same_without_the_judge():
    pairs, judge = _run(_config(), judge_labels=["narrower"])
    p = _pair(pairs, "1.1", "cusum")
    assert (p["label"], p["label_source"]) == ("same", "auto")
    assert p["distance"] <= 0.02


def test_pair_in_the_band_goes_to_the_judge_with_graded_label_and_reason():
    pairs, judge = _run(_config(), judge_labels=["narrower"] * 10)
    p = _pair(pairs, "1.2", "hotelling")
    assert 0.02 < p["distance"] <= 0.5
    assert p["label_source"] == "judge"
    assert p["label"] in gt_match.LABELS and p["reason"].startswith("because")
    assert judge.calls


def test_lower_threshold_zero_never_labels_same_without_the_judge():
    pairs, judge = _run(_config(lower_threshold=0.0), judge_labels=["related"] * 10)
    p = _pair(pairs, "1.1", "cusum")
    assert p["label_source"] == "judge" and p["label"] == "related"


def test_pair_above_the_upper_threshold_is_different_without_the_judge():
    pairs, _ = _run(_config(upper_threshold=0.3), judge_labels=["same"] * 10)
    p = _pair(pairs, "1.1", "hotelling")  # 55 degrees: ~0.43
    assert (p["label"], p["label_source"]) == ("different", "auto")


def test_every_pair_is_labeled_exactly_once_and_unattached_options_are_left_out():
    pairs, _ = _run(_config(), judge_labels=["related"] * 10)
    keys = [(p["system_id"], p["gt_id"]) for p in pairs]
    assert len(keys) == len(set(keys)) == 2 * 2  # two candidate values x two attached options
    assert all(p["gt_id"] != "orphan" for p in pairs)


def test_invalid_judge_label_is_retried_once_then_recorded_as_different_with_a_warning():
    config = _config(lower_threshold=0.0, upper_threshold=2.0, max_candidates=1)
    clusters = [dict(CLUSTERS[0], values=[CLUSTERS[0]["values"][1]])]
    judge = FakeJudgeModel(["maybe", "kinda"] + ["same"] * 10)
    system = gt_match.system_values(clusters)
    options = gt_match.ground_truth_options(GT)
    pairs = asyncio.run(gt_match.label_pairs(system, options, fake_embedder(VECTORS), judge, config))
    first = [p for p in pairs if p["label_source"] == "judge"][0]
    assert first["label"] == "different" and "invalid" in first["warning"]
    assert len(judge.calls) >= 2


def test_judge_presentation_order_is_seeded_and_recorded():
    config = _config(lower_threshold=0.0, upper_threshold=2.0)
    a, _ = _run(config, judge_labels=["same"] * 10)
    b, _ = _run(config, judge_labels=["same"] * 10)
    orders = [p["order"] for p in a if p["label_source"] == "judge"]
    assert orders and set(orders) <= {"system_first", "gt_first"}
    assert orders == [p["order"] for p in b if p["label_source"] == "judge"]


def test_broader_and_narrower_are_expressed_from_the_system_value_side():
    assert gt_match.orient_label("broader", "system_first") == "broader"
    assert gt_match.orient_label("broader", "gt_first") == "narrower"
    assert gt_match.orient_label("narrower", "gt_first") == "broader"
    assert gt_match.orient_label("related", "gt_first") == "related"


def test_cached_judge_result_is_reused_without_a_second_call(tmp_path):
    config = _config(lower_threshold=0.0, upper_threshold=2.0, cache_path=str(tmp_path / "cache.json"))
    cache = gt_match.JudgeCache(config.cache_path)
    _, judge1 = _run(config, judge_labels=["same"] * 10, cache=cache)
    cache.save()
    cache2 = gt_match.JudgeCache(config.cache_path)
    pairs, judge2 = _run(config, judge_labels=["different"] * 10, cache=cache2)
    assert judge1.calls and not judge2.calls
    assert all(p["label"] == "same" for p in pairs if p["label_source"] == "judge")
    assert json.loads((tmp_path / "cache.json").read_text())


def test_outcome_values_are_excluded_by_default_and_included_with_the_option():
    ids = [v.id for v in gt_match.system_values(CLUSTERS)]
    assert ids == ["1.1", "1.2"]
    ids = [v.id for v in gt_match.system_values(CLUSTERS, include_outcomes=True)]
    assert ids == ["1.1", "1.2", "1.3"]


@pytest.mark.parametrize("matching, message", [(None, "not set"), ("anthropic/claude", "OpenAI")])
def test_unset_or_non_openai_matching_llm_stops_the_run(matching, message):
    with pytest.raises(gt_match.MatcherError, match=message):
        gt_match.check_matching_llm(matching)


def test_matching_llm_equal_to_another_role_runs_with_a_warning():
    config = _config(matching_llm="openai/gpt-x", generation_llm="openai/gpt-x", evaluation_llm="openai/gpt-y")
    assert gt_match.check_matching_llm(config.matching_llm) == "gpt-x"
    warnings = gt_match.llm_warnings(config)
    assert len(warnings) == 1 and "generation_llm and models.matching_llm" in warnings[0]
    assert gt_match.llm_warnings(_config()) == []


def test_llm_roles_from_yaml_reach_the_matcher(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("models:\n  generation_llm: openai/gen\n  evaluation_llm: openai/eval\n"
                   "  matching_llm: openai/match\n  embedding: openai/emb\nmatcher:\n  lower_threshold: 0.3\n")
    config = gt_match.MatcherConfig.from_settings(load_settings(str(cfg)))
    assert (config.matching_llm, config.generation_llm, config.evaluation_llm, config.embedding) == \
        ("openai/match", "openai/gen", "openai/eval", "openai/emb")
    assert config.lower_threshold == 0.3


def test_legacy_model_keys_are_read_with_a_deprecation_warning_and_new_keys_win(tmp_path, caplog):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("models:\n  model: openai/gen\n  fast_llm: openai/fast\n"
                   "evaluation:\n  judge_model: openai/eval\nmatcher:\n  judge_model: openai/match\n")
    with caplog.at_level("WARNING"):
        settings = load_settings(str(cfg))
    m = settings.models
    assert (m.generation_llm, m.evaluation_llm, m.matching_llm) == ("openai/gen", "openai/eval", "openai/match")
    assert "deprecated" in caplog.text and "fast_llm" in caplog.text

    cfg.write_text("models:\n  generation_llm: openai/new\n  model: openai/old\n")
    assert load_settings(str(cfg)).models.generation_llm == "openai/new"


def test_camel_case_names_are_serialized_with_spaces_and_their_parent():
    options = gt_match.ground_truth_options(GT)
    cusum = next(o for o in options if o.id == "cusum")
    assert cusum.text == "Reward Degradation Test › CUSUM Sequential Test: Cumulative sums"
    value = gt_match.system_values(CLUSTERS)[0]
    assert value.text == "Drift Test › CUSUM chart: cumulative sums"


def test_judge_instructions_compare_options_regardless_of_their_decisions():
    steps = " ".join(gt_match.JUDGE_STEPS).lower()
    assert "regardless" in steps and "decision" in steps
    prompt = gt_match.build_judge_prompt("A › X: x", "B › X: x")
    assert "Item 1" in prompt and "Item 2" in prompt
    assert "system" not in prompt.lower() and "ground truth" not in prompt.lower()


def test_ground_truth_options_merge_views_and_keep_view_membership():
    model = json.loads(json.dumps(GT["paper"]))
    model["view"] = "model"
    model["options"].append({"id": "naive", "name": "Naive Mean", "decision_ids": ["add4"], "description": "",
                             "description_source": "", "source": "x"})
    options = gt_match.ground_truth_options({"paper": GT["paper"], "model": model})
    views = {o.id: o.views for o in options}
    assert views == {"cusum": {"paper", "model"}, "hotelling": {"paper", "model"}, "naive": {"model"}}


# ------------------------------------------------------- embeddings-only mode

def test_embeddings_mode_labels_by_distance_alone_without_the_judge():
    config = _config(mode="embeddings", same_threshold=0.05, upper_threshold=0.2, embedding_one_to_one=False)
    pairs, judge = _run(config, judge_labels=["same"] * 10)
    assert not judge.calls
    assert (_pair(pairs, "1.1", "cusum")["label"], _pair(pairs, "1.1", "cusum")["label_source"]) == ("same", "embedding")
    assert _pair(pairs, "1.2", "hotelling")["label"] == "related"     # 0.094: in the band
    assert _pair(pairs, "1.1", "hotelling")["label"] == "different"   # 0.426: beyond upper


def test_embeddings_mode_one_to_one_keeps_one_same_pair_per_item():
    config = _config(mode="embeddings", same_threshold=0.15, upper_threshold=0.5, embedding_one_to_one=True)
    pairs, _ = _run(config)
    same = [(p["system_id"], p["gt_id"]) for p in pairs if p["label"] == "same"]
    assert sorted(same) == [("1.1", "cusum"), ("1.2", "hotelling")]
    assert _pair(pairs, "1.2", "cusum")["label"] == "related"   # 0.109 <= 0.15 but its option went to 1.1


def test_unknown_mode_is_rejected():
    with pytest.raises(gt_match.MatcherError, match="mode"):
        gt_match.check_mode("fuzzy")


# ------------------------------------------------------ judge-mode branches

def test_borderline_pair_outside_both_neighbourhoods_is_auto_rank_different_without_the_judge():
    # max_candidates=1: 1.1 <-> cusum and 1.2 <-> hotelling are mutual nearest neighbours.
    config = _config(lower_threshold=0.0, upper_threshold=2.0, max_candidates=1)
    pairs, judge = _run(config, judge_labels=["same"] * 10)
    for sys_id, gt_id in (("1.1", "hotelling"), ("1.2", "cusum")):
        p = _pair(pairs, sys_id, gt_id)
        assert (p["label"], p["label_source"]) == ("different", "auto_rank")
    judged = {(p["system_id"], p["gt_id"]) for p in pairs if p["label_source"] == "judge"}
    assert judged == {("1.1", "cusum"), ("1.2", "hotelling")}
    assert len(judge.calls) == 2


def test_invalid_judge_label_retried_once_then_a_valid_label_is_kept_without_a_warning():
    config = _config(lower_threshold=0.0, upper_threshold=2.0)
    system = gt_match.system_values([dict(CLUSTERS[0], values=[CLUSTERS[0]["values"][1]])])
    options = [o for o in gt_match.ground_truth_options(GT) if o.id == "hotelling"]
    judge = FakeJudgeModel(["maybe", "same"])
    pairs = asyncio.run(gt_match.label_pairs(system, options, fake_embedder(VECTORS), judge, config))
    assert len(pairs) == 1
    assert (pairs[0]["label"], pairs[0]["label_source"], pairs[0]["warning"]) == ("same", "judge", "")
    assert len(judge.calls) == 2


def test_judge_labels_are_oriented_from_the_system_value_side_end_to_end():
    pairs, _ = _run(_config(lower_threshold=0.0, upper_threshold=2.0), judge_labels=["broader"] * 10)
    judged = [p for p in pairs if p["label_source"] == "judge"]
    assert judged
    for p in judged:
        assert p["raw_label"] == "broader"
        assert p["label"] == gt_match.orient_label("broader", p["order"])
