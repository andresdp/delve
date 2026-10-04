"""Static parsing of the C2 CodeableModels model in benchmark/parse_c2_model.py (no execution)."""

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmark"))
_spec = importlib.util.spec_from_file_location("parse_c2_model", ROOT / "benchmark" / "parse_c2_model.py")
parse_c2_model = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parse_c2_model)
import gt_format  # noqa: E402  (loaded from benchmark/ above)

METAMODEL = textwrap.dedent('''
    from codeable_models import CMetaclass, CStereotype
    decision = CMetaclass("Decision")
    practice = CMetaclass("Practice")
    force = CMetaclass("Force")
    force_impact_type = CStereotype("Force Impact Type")
    positive = CStereotype("+", superclasses=force_impact_type)
    negative = CStereotype("-", superclasses=force_impact_type)
    design_solution_dependency_type = CStereotype("Design Solution Dependency Type")
    enables = CStereotype("Enables", superclasses=design_solution_dependency_type)
    solutions_to_next_decisions_relation_type = CStereotype("Solutions To Decisions Relation Type")
    mandatory_next = CStereotype("Mandatory Next", superclasses=solutions_to_next_decisions_relation_type)
    constrains = CStereotype("Constrains", superclasses=solutions_to_next_decisions_relation_type)
    enables_next_decision = CStereotype("Enables", superclasses=solutions_to_next_decisions_relation_type)
''')

MODEL = textwrap.dedent('''
    import module_that_does_not_exist
    raise SystemExit("the parser must never execute this file")
    from codeable_models import CClass, add_links

    def add_force_relations(definition):
        for pr in definition:
            add_links({pr: pr}, role_name="forces")

    latency_force = CClass(force, "DetectionLatency")
    cost_force = CClass(
        force, "AlarmCost"
    )
    latency_force = latency_force

    cusum_option = CClass(practice, "CUSUM Sequential Test")
    mean_option = CClass(practice, "Naive Simple Mean")
    shared_option = CClass(practice, "Multi-Armed Bandit Integration")
    orphan_option = CClass(practice, "Action Failure Rate Monitoring")

    add_force_relations({
        cusum_option: {latency_force: positive},
        mean_option: {latency_force: negative, cost_force: positive},
    })
    orphan_impacts = {orphan_option: {cost_force: positive}}
    add_force_relations(orphan_impacts)

    stats_alias = cusum_option
    add1 = CClass(decision, "Test Statistic Selection")
    add2 = CClass(decision, "Exploration Strategy")
    add_decision_option_link(add1, stats_alias, option_description="Cumulative sums")
    add_decision_option_link(add1, mean_option,
                             "Compare recent mean")
    add_decision_option_link(add1, shared_option, option_description="Use bandits")
    add_decision_option_link(add2, shared_option, option_description="Use bandits")

    add_links({add1: add2}, role_name="next decision",
              stereotype_instances=[constrains, mandatory_next, enables_next_decision],
              label="test choice constrains exploration")
    add_links({add2: add1}, role_name="next decision", stereotype_instances=[constrains])
''')

MEMO = textwrap.dedent('''
    # Catalogue

    ## ADD 1: Test Statistic Selection

    **Question.** Which test detects degradation?

    **Key trade‑off.** Speed vs. false alarms.

    ### Decision Options

    | Option | Brief Description |
    | --- | --- |
    | CUSUM Sequential Test | Cumulative-sum change detection. |
    | Naive Simple Mean | Compare the recent mean reward to a baseline. |

    ### Decision Drivers

    | Driver | Impact |
    | --- | --- |
    | DetectionLatency | Favours sequential tests. |
    | UnknownDriver | Not in the model. |

    ## ADD 2: Exploration Strategy

    **Question.** How to explore safely?

    ### Decision Options

    | Option | Brief Description |
    | --- | --- |
    | Multi‑Armed Bandit Integration | Bandits for low-risk exploration. |

    ### Decision Drivers

    | Driver | Impact |
    | --- | --- |
    | AlarmCost | Penalises noisy exploration. |
    | AlarmCost (deployment‑time) | Also matters at deployment. |
''')


@pytest.fixture
def view():
    stereotypes = parse_c2_model.parse_metamodel(METAMODEL)
    model = parse_c2_model.parse_model(MODEL, stereotypes)
    memo = parse_c2_model.parse_memo(MEMO)
    return parse_c2_model.build_view(model, memo, provenance={"source": "synthetic"})


def _by_id(items):
    return {item["id"]: item for item in items}


def test_synthetic_model_parses_into_a_valid_view(view):
    errors, _ = gt_format.validate(view)
    assert errors == []
    decisions = _by_id(view["decisions"])
    options = _by_id(view["options"])
    forces = _by_id(view["forces"])
    assert set(decisions) == {"add1", "add2"}
    assert set(options) == {"cusum_sequential_test", "naive_simple_mean", "multi_armed_bandit_integration",
                            "action_failure_rate_monitoring"}
    assert set(forces) == {"detection_latency", "alarm_cost"}
    assert decisions["add1"]["decision_type"] == "unspecified"
    assert decisions["add1"]["question"] == "Which test detects degradation?"
    impacts = {(i["option_id"], i["force_id"]): i["impact"] for i in view["impacts"]}
    assert impacts == {
        ("cusum_sequential_test", "detection_latency"): "+",
        ("naive_simple_mean", "detection_latency"): "-",
        ("naive_simple_mean", "alarm_cost"): "+",
        ("action_failure_rate_monitoring", "alarm_cost"): "+",
    }


def test_alias_resolves_to_the_original_element(view):
    options = _by_id(view["options"])
    assert options["cusum_sequential_test"]["decision_ids"] == ["add1"]
    assert options["cusum_sequential_test"]["description"] == "Cumulative sums"
    assert options["cusum_sequential_test"]["description_source"] == "model"


def test_positional_third_argument_is_the_description(view):
    mean = _by_id(view["options"])["naive_simple_mean"]
    assert mean["description"] == "Compare recent mean"
    assert mean["description_source"] == "model_positional"


def test_option_linked_to_two_decisions_keeps_one_id(view):
    shared = [o for o in view["options"] if o["name"] == "Multi-Armed Bandit Integration"]
    assert len(shared) == 1
    assert shared[0]["decision_ids"] == ["add1", "add2"]


def test_memo_names_with_non_breaking_hyphens_match_model_names():
    assert parse_c2_model.normalize_name("Multi‑Armed  Bandit Integration") == \
        parse_c2_model.normalize_name("multi-armed bandit integration")
    memo = parse_c2_model.parse_memo(MEMO)
    section = memo[parse_c2_model.normalize_name("Exploration Strategy")]
    assert parse_c2_model.normalize_name("Multi-Armed Bandit Integration") in section["options"]


def test_memo_description_is_the_fallback_when_the_model_has_none():
    stereotypes = parse_c2_model.parse_metamodel(METAMODEL)
    source = MODEL.replace('add_decision_option_link(add1, stats_alias, option_description="Cumulative sums")',
                           "add_decision_option_link(add1, stats_alias)")
    view = parse_c2_model.build_view(parse_c2_model.parse_model(source, stereotypes),
                                     parse_c2_model.parse_memo(MEMO), provenance={})
    cusum = _by_id(view["options"])["cusum_sequential_test"]
    assert cusum["description"] == "Cumulative-sum change detection."
    assert cusum["description_source"] == "memo"


def test_unattached_option_takes_its_description_from_any_memo_section():
    stereotypes = parse_c2_model.parse_metamodel(METAMODEL)
    memo_text = MEMO.replace("| Naive Simple Mean |", "| Action Failure Rate Monitoring | Track failed actions. |\n| Naive Simple Mean |")
    view = parse_c2_model.build_view(parse_c2_model.parse_model(MODEL, stereotypes),
                                     parse_c2_model.parse_memo(memo_text), provenance={})
    orphan = _by_id(view["options"])["action_failure_rate_monitoring"]
    assert (orphan["description"], orphan["description_source"]) == ("Track failed actions.", "memo")


def test_unattached_option_is_recorded_and_reported(view):
    orphan = _by_id(view["options"])["action_failure_rate_monitoring"]
    assert orphan["decision_ids"] == [] and orphan["unattached"] is True
    assert orphan["description"] == ""  # not in the synthetic memo
    discrepancies = view["provenance"]["discrepancies"]
    assert any("Action Failure Rate Monitoring" in d and "unattached" in d for d in discrepancies)


def test_stereotypes_resolve_by_kind():
    stereotypes = parse_c2_model.parse_metamodel(METAMODEL)
    assert stereotypes["positive"] == {"label": "+", "kind": "impact"}
    assert stereotypes["enables_next_decision"] == {"label": "Enables", "kind": "next_decision"}
    assert stereotypes["enables"] == {"label": "Enables", "kind": "dependency"}


def test_decision_links_keep_stereotype_lists_and_labels(view):
    links = {(lk["from"], lk["to"]): lk for lk in view["decision_links"]}
    assert links[("add1", "add2")]["stereotypes"] == ["Constrains", "Mandatory Next", "Enables"]
    assert links[("add1", "add2")]["label"] == "test choice constrains exploration"
    assert links[("add2", "add1")]["label"] == ""


def test_per_decision_force_text_comes_from_the_memo(view):
    records = [(r["decision_id"], r["force_id"], r["text"]) for r in view["decision_forces"]]
    assert ("add1", "detection_latency", "Favours sequential tests.") in records
    assert ("add2", "alarm_cost", "Penalises noisy exploration.") in records
    assert ("add2", "alarm_cost", "Also matters at deployment.") in records
    assert all(f["description"] == "" for f in view["forces"])
    assert any("UnknownDriver" in d for d in view["provenance"]["discrepancies"])


def test_dynamic_construct_stops_the_parser():
    stereotypes = parse_c2_model.parse_metamodel(METAMODEL)
    dynamic = MODEL + "\nfor name in ['A', 'B']:\n    CClass(practice, name)\n"
    with pytest.raises(parse_c2_model.UnsupportedConstruct, match="CClass"):
        parse_c2_model.parse_model(dynamic, stereotypes)


def test_generated_view_cross_check_lists_differences(view):
    plantuml = textwrap.dedent('''
        @startuml
        class "<b>Test Statistic Selection</b>\\n<b>: Decision</b>" as __1
        class "<b>CUSUM Sequential Test : Practice</b>" as __2
        class "<b>Naive Simple Mean : Practice</b>" as __3
        class "<b>Extra Practice : Practice</b>" as __4
        class "<b>DetectionLatency : Force</b>" as __5
        __1 --> __2: <<Option>>\\n{description = "Cumulative\\nsums"}
        __2 --> __5: <<+>>
        @enduml
    ''')
    generated = parse_c2_model.parse_plantuml(plantuml)
    assert generated["option_names"] >= {"CUSUM Sequential Test", "Extra Practice"}
    assert ("Test Statistic Selection", "CUSUM Sequential Test") in generated["option_links"]
    diffs = parse_c2_model.cross_check(view, generated)
    assert any("Extra Practice" in d for d in diffs)
    assert any("Multi-Armed Bandit Integration" in d for d in diffs)
