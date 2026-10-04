"""Crosswalk between a study's paper view and model view in benchmark/gt_crosswalk.py."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gt_crosswalk", ROOT / "benchmark" / "gt_crosswalk.py")
gt_crosswalk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gt_crosswalk)


def _view(view, decisions, options):
    return {
        "format_version": 1, "study": "toy", "view": view, "provenance": {},
        "decisions": [{"id": d, "name": d.upper(), "question": "", "decision_type": "unspecified",
                       "description": "", "description_source": "", "source": "x"} for d in decisions],
        "options": [{"id": o, "name": o.title(), "decision_ids": [decisions[0]], "description": "",
                     "description_source": "", "source": "x"} for o in options],
        "forces": [], "decision_forces": [], "impacts": [], "decision_links": [],
    }


def _pair():
    model = _view("model", ["add1"], ["cusum", "mean", "hotelling"])
    paper = _view("paper", ["add1"], ["cusum", "mean", "P_bootstrap"])
    return paper, model


def test_consistent_views_and_crosswalk_pass():
    paper, model = _pair()
    rows = gt_crosswalk.build_crosswalk(paper, model)
    status = {(r["kind"], r["id"]): r["status"] for r in rows}
    assert status == {
        ("decision", "add1"): "paper+model",
        ("option", "cusum"): "paper+model",
        ("option", "mean"): "paper+model",
        ("option", "hotelling"): "model only",
        ("option", "P_bootstrap"): "paper only",
    }
    assert gt_crosswalk.check_crosswalk(paper, model, rows) == []


def test_crosswalk_that_omits_an_element_is_reported():
    paper, model = _pair()
    rows = [r for r in gt_crosswalk.build_crosswalk(paper, model) if r["id"] not in ("hotelling", "P_bootstrap")]
    errors = gt_crosswalk.check_crosswalk(paper, model, rows)
    assert any("hotelling" in e and "missing from the crosswalk" in e for e in errors)
    assert any("P_bootstrap" in e and "missing from the crosswalk" in e for e in errors)


def test_paper_and_model_element_missing_from_one_view_is_reported():
    paper, model = _pair()
    rows = gt_crosswalk.build_crosswalk(paper, model)
    for row in rows:
        if row["id"] == "hotelling":
            row["status"] = "paper+model"
    errors = gt_crosswalk.check_crosswalk(paper, model, rows)
    assert any("hotelling" in e and "not in the paper view" in e for e in errors)


def test_paper_only_element_reusing_a_model_id_is_reported():
    paper, model = _pair()
    paper["options"].append(dict(paper["options"][0], id="hotelling"))
    rows = gt_crosswalk.build_crosswalk(paper, model)
    for row in rows:
        if row["id"] == "hotelling":
            row["status"] = "paper only"
    errors = gt_crosswalk.check_crosswalk(paper, model, rows)
    assert any("hotelling" in e and "reuses a model id" in e for e in errors)


def test_paper_only_id_without_prefix_and_unknown_status_are_reported():
    paper, model = _pair()
    paper["options"][2]["id"] = "bootstrap"
    rows = gt_crosswalk.build_crosswalk(paper, model)
    rows.append({"kind": "option", "id": "ghost", "name": "Ghost", "status": "maybe", "note": ""})
    errors = gt_crosswalk.check_crosswalk(paper, model, rows)
    assert any("bootstrap" in e and "'P'" in e for e in errors)
    assert any("ghost" in e and "'maybe'" in e for e in errors)


def test_csv_round_trip(tmp_path):
    paper, model = _pair()
    rows = gt_crosswalk.build_crosswalk(paper, model)
    path = tmp_path / "gt_crosswalk.csv"
    gt_crosswalk.write_crosswalk(path, rows)
    assert gt_crosswalk.read_crosswalk(path) == rows
