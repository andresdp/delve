"""taxonomy.relation_types / max_relations_per_dimension: defaults, YAML, validation."""

import pytest

from taxonomy_generator.configuration import Configuration, init_settings
from taxonomy_generator.settings import load_settings


def _yaml(tmp_path, body):
    cfg = tmp_path / "c.yaml"
    cfg.write_text(body)
    return str(cfg)


def test_defaults_are_four_types_and_a_cap_of_three(tmp_path):
    s = load_settings(_yaml(tmp_path, "taxonomy:\n  name: t\n"))
    assert s.taxonomy.relation_types == ("requires", "affects", "constrains", "co_occurs_with")
    assert s.taxonomy.max_relations_per_dimension == 3


def test_yaml_values_reach_the_configuration(tmp_path):
    path = _yaml(tmp_path, "taxonomy:\n  relation_types: [requires, refines]\n  max_relations_per_dimension: null\n")
    try:
        init_settings(path)
        c = Configuration.from_runnable_config({"configurable": {}})
        assert tuple(c.relation_types) == ("requires", "refines")
        assert c.max_relations_per_dimension is None
    finally:
        init_settings(None)


@pytest.mark.parametrize("body, match", [
    ("taxonomy:\n  relation_types: [requires, enables]\n", "relation_types"),
    ("taxonomy:\n  relation_types: []\n", "relation_types"),
    ("taxonomy:\n  max_relations_per_dimension: 0\n", "max_relations_per_dimension"),
])
def test_invalid_values_are_rejected(tmp_path, body, match):
    with pytest.raises(ValueError, match=match):
        load_settings(_yaml(tmp_path, body))
