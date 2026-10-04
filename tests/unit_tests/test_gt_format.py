"""Ground-truth format and validator in benchmark/gt_format.py."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gt_format", ROOT / "benchmark" / "gt_format.py")
gt_format = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gt_format)


def _minimal() -> dict:
    """One decision, two options, one force, one impact, one link with two stereotypes."""
    return {
        "format_version": 1,
        "study": "toy",
        "view": "model",
        "provenance": {"source": "synthetic"},
        "decisions": [
            {"id": "d1", "name": "Drift Test", "question": "Which test detects drift?",
             "decision_type": "single", "description": "Pick a drift test.",
             "description_source": "paper", "source": "p. 3"},
            {"id": "d2", "name": "Response", "question": "", "decision_type": "multiple",
             "description": "React to drift.", "description_source": "paper", "source": "p. 4"},
        ],
        "options": [
            {"id": "cusum", "name": "CUSUM", "decision_ids": ["d1"], "description": "Cumulative sums.",
             "description_source": "model", "source": "model.py:10"},
            {"id": "mean", "name": "Mean Test", "decision_ids": ["d1"], "description": "Compare means.",
             "description_source": "model", "source": "model.py:11"},
        ],
        "forces": [
            {"id": "latency", "name": "Detection Latency", "description": "", "description_source": "",
             "source": "model.py:5"},
        ],
        "decision_forces": [
            {"decision_id": "d1", "force_id": "latency", "text": "Detect fast.", "source": "memo §4"},
        ],
        "impacts": [
            {"option_id": "cusum", "force_id": "latency", "impact": "+", "source": "model.py:20"},
        ],
        "decision_links": [
            {"from": "d1", "to": "d2", "stereotypes": ["Constrains", "Enables"], "label": "test feeds response",
             "source": "model.py:30"},
        ],
    }


def _errors(data):
    return gt_format.validate(data)[0]


def _warnings(data):
    return gt_format.validate(data)[1]


def test_minimal_file_validates_without_errors_or_warnings():
    errors, warnings = gt_format.validate(_minimal())
    assert errors == []
    assert warnings == []


def test_duplicate_option_id_is_reported_with_both_locations():
    data = _minimal()
    data["options"][1]["id"] = "cusum"
    errors = _errors(data)
    assert any("duplicate id 'cusum'" in e and "options[0]" in e and "options[1]" in e for e in errors)


def test_id_shared_across_element_kinds_is_a_duplicate():
    data = _minimal()
    data["forces"][0]["id"] = "d1"
    data["decision_forces"][0]["force_id"] = "d1"
    data["impacts"][0]["force_id"] = "d1"
    errors = _errors(data)
    assert any("duplicate id 'd1'" in e and "decisions[0]" in e and "forces[0]" in e for e in errors)


def test_impact_pointing_to_unknown_force_is_reported():
    data = _minimal()
    data["impacts"][0]["force_id"] = "nope"
    assert any("impacts[0]" in e and "unknown force 'nope'" in e for e in _errors(data))


def test_dangling_decision_references_are_reported():
    data = _minimal()
    data["options"][0]["decision_ids"] = ["d9"]
    data["decision_links"][0]["to"] = "d8"
    errors = _errors(data)
    assert any("options[0]" in e and "unknown decision 'd9'" in e for e in errors)
    assert any("decision_links[0]" in e and "unknown decision 'd8'" in e for e in errors)


def test_unknown_impact_stereotype_is_rejected():
    data = _minimal()
    data["impacts"][0]["impact"] = "+++"
    assert any("impacts[0]" in e and "'+++'" in e for e in _errors(data))


def test_unknown_link_stereotype_and_decision_type_are_rejected():
    data = _minimal()
    data["decision_links"][0]["stereotypes"] = ["Constrains", "Makes Coffee"]
    data["decisions"][0]["decision_type"] = "several"
    errors = _errors(data)
    assert any("decision_links[0]" in e and "'Makes Coffee'" in e for e in errors)
    assert any("decisions[0]" in e and "'several'" in e for e in errors)


def test_unspecified_decision_type_validates_with_a_warning():
    data = _minimal()
    data["decisions"][0]["decision_type"] = "unspecified"
    errors, warnings = gt_format.validate(data)
    assert errors == []
    assert any("decisions[0]" in w and "unspecified" in w for w in warnings)


def test_empty_option_description_validates_with_a_warning():
    data = _minimal()
    data["options"][1]["description"] = ""
    data["options"][1]["description_source"] = ""
    errors, warnings = gt_format.validate(data)
    assert errors == []
    assert any("options[1]" in w and "description" in w for w in warnings)


def test_option_without_decision_must_be_marked_unattached():
    data = _minimal()
    data["options"][1]["decision_ids"] = []
    assert any("options[1]" in e and "unattached" in e for e in _errors(data))
    data["options"][1]["unattached"] = True
    errors, warnings = gt_format.validate(data)
    assert errors == []
    assert any("options[1]" in w and "unattached" in w for w in warnings)


def test_missing_source_reference_and_bad_ids_are_errors():
    data = _minimal()
    data["options"][0]["source"] = ""
    data["decisions"][1]["id"] = "has space"
    data["decision_links"][0]["from"] = "has space"
    errors = _errors(data)
    assert any("options[0]" in e and "source" in e for e in errors)
    assert any("decisions[1]" in e and "malformed id" in e for e in errors)


def test_unknown_view_and_description_source_are_rejected():
    data = _minimal()
    data["view"] = "draft"
    data["options"][0]["description_source"] = "llm"
    errors = _errors(data)
    assert any("view" in e and "'draft'" in e for e in errors)
    assert any("options[0]" in e and "'llm'" in e for e in errors)


def test_missing_top_level_list_is_reported():
    data = _minimal()
    del data["forces"]
    assert any("forces" in e for e in _errors(data))


def test_load_raises_on_errors_and_returns_data_and_warnings(tmp_path):
    good = tmp_path / "gt_model.json"
    good.write_text(json.dumps(_minimal()), encoding="utf-8")
    data, warnings = gt_format.load_ground_truth(good)
    assert data["study"] == "toy" and warnings == []

    bad_data = copy.deepcopy(_minimal())
    bad_data["impacts"][0]["impact"] = "+++"
    bad = tmp_path / "gt_bad.json"
    bad.write_text(json.dumps(bad_data), encoding="utf-8")
    with pytest.raises(gt_format.GroundTruthError, match=r"\+\+\+"):
        gt_format.load_ground_truth(bad)


def test_command_line_check_exit_codes(tmp_path, capsys):
    good = tmp_path / "gt_model.json"
    good.write_text(json.dumps(_minimal()), encoding="utf-8")
    bad_data = _minimal()
    bad_data["options"][0]["decision_ids"] = ["d9"]
    bad = tmp_path / "gt_paper.json"
    bad.write_text(json.dumps(bad_data), encoding="utf-8")
    assert gt_format.main([str(good)]) == 0
    assert gt_format.main([str(good), str(bad)]) == 1
    out = capsys.readouterr().out
    assert "unknown decision 'd9'" in out
