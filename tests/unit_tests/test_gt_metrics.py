"""Ground-truth matcher, part 2: dimension alignment, metrics per view and outputs (no API calls)."""

import csv
import json

import numpy as np
import pytest

from taxonomy_generator.evaluation import gt_match


def _gt(view, decisions, options):
    """decisions: {id: name}; options: {id: (name, [decision ids])}."""
    return {
        "format_version": 1, "study": "toy", "view": view, "provenance": {},
        "decisions": [{"id": d, "name": n, "question": "", "decision_type": "unspecified", "description": "",
                       "description_source": "", "source": "x"} for d, n in decisions.items()],
        "options": [{"id": o, "name": n, "decision_ids": ds, "description": "", "description_source": "",
                     "source": "x"} for o, (n, ds) in options.items()],
        "forces": [], "decision_forces": [], "impacts": [], "decision_links": [],
    }


PAPER = _gt("paper", {"d1": "Drift Test", "d2": "Response"},
            {"o1": ("CUSUM", ["d1"]), "o2": ("Mean", ["d1"]), "o3": ("Rollback", ["d2"]), "o4": ("Shadow", ["d2"])})
MODEL = _gt("model", {"d1": "Drift Test", "d2": "Response", "d3": "Hacking"},
            {"o1": ("CUSUM", ["d1"]), "o2": ("Mean", ["d1"]), "o3": ("Rollback", ["d2"]), "o4": ("Shadow", ["d2"]),
             "o5": ("CoT", ["d3"]), "o6": ("Ensemble", ["d3"])})
VIEWS = {"paper": PAPER, "model": MODEL}


def _clusters(spec):
    """spec: {dim id: [value ids]}."""
    return [{"id": d, "name": f"Dim {d}", "description": "", "values": [
        {"id": v, "label": f"Value {v}", "description": "", "status": "accepted"} for v in vals]}
        for d, vals in spec.items()]


def _pairs(labels):
    """labels: {(value id, option id): label}; every other pair is 'different'."""
    return [{"system_id": s, "gt_id": o, "label": lab, "label_source": "judge", "distance": 0.1}
            for (s, o), lab in labels.items()]


def _metrics(spec, labels, min_share=0.25):
    clusters = _clusters(spec)
    return gt_match.compute_metrics(
        gt_match.system_dimensions(clusters), gt_match.system_values(clusters), VIEWS,
        gt_match.ground_truth_options(VIEWS), _pairs(labels), min_alignment_share=min_share)


def test_perfect_match_gives_f1_one_at_both_levels_and_full_placement():
    labels = {("1.1", "o1"): "same", ("1.2", "o2"): "same", ("2.1", "o3"): "same", ("2.2", "o4"): "same",
              ("3.1", "o5"): "same", ("3.2", "o6"): "same"}
    m = _metrics({"1": ["1.1", "1.2"], "2": ["2.1", "2.2"], "3": ["3.1", "3.2"]}, labels)["model"]
    assert m["option"]["f1"] == 1.0 and m["option"]["exact_recall"] == 1.0
    assert m["decision"]["strict"]["f1"] == 1.0 and m["decision"]["lenient"]["f1"] == 1.0
    assert m["placement"]["accuracy"] == 1.0


def test_no_matches_gives_zero_without_errors():
    m = _metrics({"1": ["1.1"]}, {})
    for view in ("paper", "model"):
        assert m[view]["option"]["precision"] == 0.0 and m[view]["option"]["recall"] == 0.0
        assert m[view]["option"]["f1"] == 0.0
        assert m[view]["decision"]["strict"]["recall"] == 0.0
        assert m[view]["placement"]["accuracy"] is None


def test_one_dimension_covering_two_decisions_counts_in_lenient_not_strict_alignment():
    labels = {("1.1", "o1"): "same", ("1.2", "o2"): "same", ("1.3", "o3"): "same", ("1.4", "o4"): "same"}
    m = _metrics({"1": ["1.1", "1.2", "1.3", "1.4"]}, labels)["paper"]
    assert m["decision"]["lenient"]["recall"] == 1.0
    assert m["decision"]["strict"]["recall"] == 0.5


def test_paper_view_recall_ignores_model_only_options_and_precision_leaves_out_their_matches():
    labels = {("1.1", "o1"): "same", ("3.1", "o5"): "same"}
    m = _metrics({"1": ["1.1"], "3": ["3.1", "3.2"]}, labels)
    paper, model = m["paper"]["option"], m["model"]["option"]
    assert paper["recall"] == pytest.approx(1 / 4, abs=1e-4) and model["recall"] == pytest.approx(2 / 6, abs=1e-4)
    # 3.1 matches only a model-only option: left out of paper precision and counted
    assert paper["model_only_matched_values"] == 1
    assert paper["precision"] == pytest.approx(1 / 2, abs=1e-4)   # 1.1 hit, 3.2 miss
    assert model["precision"] == pytest.approx(2 / 3, abs=1e-4)


def test_broader_and_narrower_count_for_recall_but_not_exact_recall_and_related_only_raises_the_rate():
    labels = {("1.1", "o1"): "broader", ("1.2", "o2"): "narrower", ("2.1", "o3"): "related"}
    m = _metrics({"1": ["1.1", "1.2"], "2": ["2.1"]}, labels)["paper"]["option"]
    assert m["recall"] == pytest.approx(2 / 4, abs=1e-4)
    assert m["exact_recall"] == 0.0
    assert m["related_rate"] == pytest.approx(1 / 3, abs=1e-4)
    assert m["precision"] == pytest.approx(2 / 3, abs=1e-4)


def test_value_under_a_dimension_not_aligned_with_its_option_decision_lowers_placement_not_recall():
    labels = {("1.1", "o1"): "same", ("1.2", "o2"): "same", ("1.3", "o3"): "same", ("2.1", "o4"): "same"}
    # dim 1 aligns with d1 (share 2/2) but not d2 (1/2 < 0.6); its value 1.3 matches o3 of d2.
    m = _metrics({"1": ["1.1", "1.2", "1.3"], "2": ["2.1"]}, labels, min_share=0.6)["paper"]
    assert m["option"]["recall"] == 1.0
    assert m["placement"]["accuracy"] == pytest.approx(3 / 4, abs=1e-4)


def test_outputs_contain_every_pair_with_distance_label_and_source(tmp_path):
    clusters = _clusters({"1": ["1.1"], "2": ["2.1"]})
    pairs = [{"system_id": "1.1", "system_text": "a", "gt_id": "o1", "gt_text": "b", "distance": 0.1,
              "label": "same", "label_source": "judge", "reason": "r", "order": "gt_first", "warning": ""},
             {"system_id": "2.1", "system_text": "c", "gt_id": "o3", "gt_text": "d", "distance": 0.7,
              "label": "different", "label_source": "auto", "reason": "", "order": "", "warning": ""}]
    metrics = gt_match.compute_metrics(gt_match.system_dimensions(clusters), gt_match.system_values(clusters),
                                       VIEWS, gt_match.ground_truth_options(VIEWS), pairs, min_alignment_share=0.25)
    paths = gt_match.write_outputs(tmp_path, "run", pairs, metrics, {"judge_model": "openai/j"})
    match = json.loads(paths["match"].read_text())
    assert [(p["system_id"], p["gt_id"], p["distance"], p["label"], p["label_source"]) for p in match["pairs"]] == \
        [("1.1", "o1", 0.1, "same", "judge"), ("2.1", "o3", 0.7, "different", "auto")]
    assert match["settings"]["judge_model"] == "openai/j"
    rows = list(csv.DictReader(paths["alignment"].open()))
    assert {"view", "alignment", "dimension_id", "decision_id", "share"} <= set(rows[0])
    assert json.loads(paths["metrics"].read_text())["paper"]["option"]["recall"] == pytest.approx(1 / 4, abs=1e-4)


def test_run_match_scores_a_saved_taxonomy_end_to_end_without_api_calls(tmp_path):
    import asyncio

    from taxonomy_generator.settings import load_settings

    gt = tmp_path / "gt"
    gt.mkdir()
    (gt / "gt_paper.json").write_text(json.dumps(PAPER))
    (gt / "gt_model.json").write_text(json.dumps(MODEL))
    clusters = _clusters({"1": ["1.1"], "2": ["2.1"]})
    clusters[0]["values"][0]["label"] = "CUSUM"
    taxonomy = tmp_path / "run_taxonomy_1.json"
    taxonomy.write_text(json.dumps({"iterations": [{"clusters": clusters}], "selected_clusters": clusters}))
    cfg = tmp_path / "c.yaml"
    cfg.write_text(f"models:\n  model: openai/gen\nevaluation:\n  judge_model: openai/judge\n"
                   f"matcher:\n  cache_path: {tmp_path / 'cache.json'}\n")

    def embed(texts):  # "CUSUM" texts close together, everything else spread apart
        out = []
        for t in texts:
            a = (sum(map(ord, t)) % 90) * np.pi / 180
            out.append([1.0, 0.0, 0.0] if "CUSUM" in t else [0.0, np.cos(a), np.sin(a)])
        return np.asarray(out)

    class Judge:
        async def a_generate(self, prompt, schema=None):
            return schema(label="same" if prompt.count("CUSUM") == 2 else "different", reason="r"), 0.0

        def get_model_name(self):
            return "judge"

    result = asyncio.run(gt_match.run_match(str(taxonomy), str(gt), load_settings(str(cfg)), out_dir=str(tmp_path),
                                            embed=embed, judge_model=Judge()))
    assert result["metrics"]["paper"]["option"]["recall"] == pytest.approx(0.25, abs=1e-4)
    assert result["settings"]["judge_model"] == "openai/judge"
    assert all(p.exists() for p in result["paths"].values())
    with pytest.raises(gt_match.MatcherError, match="same model"):
        asyncio.run(gt_match.run_match(str(taxonomy), str(gt), load_settings(str(cfg)), judge_override="openai/gen",
                                       embed=embed, judge_model=Judge()))
