"""The three LLM roles (generation, evaluation, matching): defaults, YAML keys and shared-model warnings."""

from taxonomy_generator.configuration import Configuration, init_settings
from taxonomy_generator.settings import (
    ModelSettings,
    load_settings,
    shared_llm_warnings,
)


def test_default_roles_are_three_different_models():
    m = ModelSettings()
    assert len({m.generation_llm, m.evaluation_llm, m.matching_llm}) == 3
    assert shared_llm_warnings(m) == []


def test_every_pair_of_roles_sharing_a_model_is_warned_about():
    m = ModelSettings(generation_llm="openai/x", evaluation_llm="openai/x", matching_llm="openai/x")
    warnings = shared_llm_warnings(m)
    assert len(warnings) == 3
    assert any("generation_llm and models.evaluation_llm" in w for w in warnings)
    # restricted to the roles a command uses
    assert len(shared_llm_warnings(m, ("generation_llm", "evaluation_llm"))) == 1


def test_provider_prefix_does_not_hide_a_shared_model():
    m = ModelSettings(generation_llm="openai/gpt-x", evaluation_llm="gpt-x")
    assert shared_llm_warnings(m, ("generation_llm", "evaluation_llm"))


def test_roles_from_yaml_reach_the_pipeline_configuration(tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("models:\n  generation_llm: openai/gen\n  evaluation_llm: openai/eval\n"
                   "  matching_llm: openai/match\n")
    assert load_settings(str(cfg)).models.matching_llm == "openai/match"
    try:
        init_settings(str(cfg))
        c = Configuration.from_runnable_config({"configurable": {}})
        assert (c.generation_llm, c.evaluation_llm, c.matching_llm) == ("openai/gen", "openai/eval", "openai/match")
        c = Configuration.from_runnable_config({"configurable": {"evaluation_llm": "openai/cli"}})
        assert c.evaluation_llm == "openai/cli"
    finally:
        init_settings(None)


def test_command_line_role_overrides_keep_only_the_flags_given():
    import argparse

    import main as main_module

    args = argparse.Namespace(generation_llm=None, evaluation_llm="openai/eval-cli", matching_llm=None)
    assert main_module._llm_role_overrides(args) == {"evaluation_llm": "openai/eval-cli"}
    assert main_module._llm_role_overrides(argparse.Namespace()) == {}


def test_evaluate_command_passes_the_evaluation_llm_flag_to_its_configuration(monkeypatch):
    import argparse
    import asyncio

    import pytest

    import main as main_module

    seen = {}

    class Stop(Exception):
        pass

    def capture(config=None):
        seen.update(config["configurable"])
        raise Stop

    monkeypatch.setattr(main_module.Configuration, "from_runnable_config", staticmethod(capture))
    args = argparse.Namespace(config=None, evaluate=["t.json"], output=None, generation_llm=None,
                              evaluation_llm="openai/eval-cli", matching_llm=None)
    with pytest.raises(Stop):
        asyncio.run(main_module._run_evaluate(args))
    assert seen == {"evaluation_llm": "openai/eval-cli"}
