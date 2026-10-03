"""Which view of a saved taxonomy seeds a run (test mode freezes the selected view)."""

import json

import pytest

from taxonomy_generator.utils import load_seed_taxonomy, resolve_seed_view

FINAL = [
    {"id": "1", "name": "Kept", "description": "", "relations": [{"target_id": "2", "type": "constrains"},
                                                                 {"target_id": "3", "type": "precondition"}]},
    {"id": "2", "name": "Dropped by selection", "description": ""},
    {"id": "3", "name": "Also kept", "description": ""},
]
SELECTED = [FINAL[0], FINAL[2]]


@pytest.fixture
def saved(tmp_path):
    path = tmp_path / "taxonomy.json"
    path.write_text(json.dumps({"iterations": [{"clusters": FINAL}], "selected_clusters": SELECTED}))
    return str(path)


def test_auto_freezes_the_selected_view_in_test_mode_and_refines_the_final_iteration_in_train_mode():
    assert resolve_seed_view("auto", "test") == "selected"
    assert resolve_seed_view(None, "test") == "selected"
    assert resolve_seed_view("auto", "train") == "final"
    assert resolve_seed_view("final", "test") == "final"
    with pytest.raises(ValueError):
        resolve_seed_view("latest", "test")


def test_selected_view_drops_relations_to_dimensions_selection_removed(saved):
    clusters = load_seed_taxonomy(saved, "selected")
    assert [c["name"] for c in clusters] == ["Kept", "Also kept"]
    assert clusters[0]["relations"] == [{"target_id": "3", "type": "precondition"}]


def test_final_view_keeps_every_dimension(saved):
    assert [c["id"] for c in load_seed_taxonomy(saved)] == ["1", "2", "3"]


def test_selected_view_falls_back_to_the_final_iteration_when_missing(tmp_path):
    path = tmp_path / "taxonomy.json"
    path.write_text(json.dumps({"iterations": [{"clusters": FINAL}]}))
    assert len(load_seed_taxonomy(str(path), "selected")) == 3
