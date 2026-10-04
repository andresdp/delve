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
    base = dict(judge_model="openai/judge-model", generator_model="openai/generator", embedding="openai/emb",
                lower_threshold=0.02, upper_threshold=0.5, max_candidates=5, include_outcomes=False,
                min_alignment_share=0.25, seed=0, cache_path=None)
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


@pytest.mark.parametrize("judge, generator, message", [
    (None, "openai/gpt-x", "judge_model is not set"),
    ("openai/gpt-x", "openai/gpt-x", "same model as the generator"),
    ("anthropic/claude", "openai/gpt-x", "OpenAI"),
])
def test_unset_judge_or_judge_equal_to_generator_stops_the_run(judge, generator, message):
    with pytest.raises(gt_match.MatcherError, match=message):
        gt_match.check_judge(judge, generator)


def test_matcher_judge_model_from_yaml_reaches_the_matcher_and_never_falls_back(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("models:\n  model: openai/gen\n  embedding: openai/emb\n"
                   "matcher:\n  judge_model: openai/judge\n  lower_threshold: 0.3\n")
    config = gt_match.MatcherConfig.from_settings(load_settings(str(cfg)))
    assert (config.judge_model, config.generator_model, config.embedding) == ("openai/judge", "openai/gen", "openai/emb")
    assert config.lower_threshold == 0.3

    cfg.write_text("models:\n  model: openai/gen\nevaluation:\n  judge_model: openai/eval-judge\n")
    config = gt_match.MatcherConfig.from_settings(load_settings(str(cfg)))
    assert config.judge_model == "openai/eval-judge"  # the pipeline's configured judge

    cfg.write_text("models:\n  model: openai/gen\n")
    config = gt_match.MatcherConfig.from_settings(load_settings(str(cfg)))
    assert config.judge_model is None
    with pytest.raises(gt_match.MatcherError):
        gt_match.check_judge(config.judge_model, config.generator_model)


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
