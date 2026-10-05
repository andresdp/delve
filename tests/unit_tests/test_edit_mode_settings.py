"""taxonomy.edit_mode / edit_max_steps: defaults, YAML, overrides, validation."""

import pytest

from taxonomy_generator.configuration import Configuration, init_settings
from taxonomy_generator.settings import EDIT_MODES, load_settings


def _yaml(tmp_path, body):
    cfg = tmp_path / "c.yaml"
    cfg.write_text(body)
    return str(cfg)


def test_defaults_are_rewrite_and_twelve_steps(tmp_path):
    s = load_settings(_yaml(tmp_path, "taxonomy:\n  name: t\n"))
    assert s.taxonomy.edit_mode == "rewrite"
    assert s.taxonomy.edit_max_steps == 12
    assert EDIT_MODES == ("rewrite", "rewrite_restore", "tools")


@pytest.mark.parametrize("mode", ["tools", "rewrite_restore"])
def test_edit_mode_from_yaml_reaches_the_configuration(tmp_path, mode):
    path = _yaml(tmp_path, f"taxonomy:\n  edit_mode: {mode}\n  edit_max_steps: 3\n")
    try:
        init_settings(path)
        c = Configuration.from_runnable_config({"configurable": {}})
        assert (c.edit_mode, c.edit_max_steps) == (mode, 3)
        c = Configuration.from_runnable_config({"configurable": {"edit_mode": "rewrite"}})
        assert c.edit_mode == "rewrite"
    finally:
        init_settings(None)


def test_unknown_edit_mode_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="taxonomy.edit_mode must be one of"):
        load_settings(_yaml(tmp_path, "taxonomy:\n  edit_mode: patch\n"))


def test_edit_max_steps_must_be_positive(tmp_path):
    with pytest.raises(ValueError, match="edit_max_steps"):
        load_settings(_yaml(tmp_path, "taxonomy:\n  edit_max_steps: 0\n"))
