"""Relation types between dimensions: reading sentences, direction checks, legacy names and clean-up."""

import pytest

from taxonomy_generator.relations import (
    DEFAULT_RELATION_TYPES,
    RELATION_KINDS,
    RELATION_TYPES,
    check_reading,
    clean_relations,
    normalize_type,
    relation_problem,
    render_reading,
)

A, B = "Data Profiling and Validation", "Training Update Algorithm"


def _dims(*specs):
    return [{"id": i, "name": n, "description": "", "relations": list(r), "values": []} for i, n, r in specs]


# ---------------------------------------------------------------- table and readings


def test_table_covers_every_type_and_defaults_exclude_refines():
    assert set(RELATION_KINDS) == set(RELATION_TYPES)
    assert DEFAULT_RELATION_TYPES == ("requires", "affects", "constrains", "co_occurs_with")
    assert "refines" in RELATION_TYPES and "refines" not in DEFAULT_RELATION_TYPES
    assert not RELATION_KINDS["co_occurs_with"].directed
    assert all(RELATION_KINDS[t].directed for t in ("requires", "affects", "constrains", "refines"))


@pytest.mark.parametrize("rtype", RELATION_TYPES)
def test_canonical_reading_passes_its_own_check(rtype):
    sentence = render_reading(B, rtype, A)
    assert B in sentence and A in sentence
    assert check_reading(sentence, B, A, rtype) is None


def test_requires_reading_wording():
    assert render_reading(B, "requires", A) == f"{B} requires {A} to be decided first"


def test_check_reading_rejects_swapped_names_and_suggests_the_reverse():
    swapped = render_reading(A, "requires", B)  # names in the wrong order for source=B, target=A
    problem = check_reading(swapped, B, A, "requires")
    assert problem and "swap" in problem.lower()


def test_check_reading_rejects_wrong_verb_and_missing_names():
    assert check_reading(f"{B} affects the outcomes of {A}", B, A, "requires")
    assert check_reading(f"{B} requires something else first", B, A, "requires")
    assert check_reading("", B, A, "requires")


def test_check_reading_tolerates_case_punctuation_and_small_name_variations():
    assert check_reading(f"training update algorithm requires data profiling & validation to be decided first.",
                         B, A, "requires") is None
    assert check_reading("Choices on the Training Update Algorithm affect the outcomes of data profiling",
                         B, A, "affects") is None


def test_co_occurs_reading_accepts_either_name_order():
    assert check_reading(f"{A} and {B} are usually decided together", B, A, "co_occurs_with") is None


def test_normalize_type_maps_legacy_names():
    assert normalize_type("precondition") == "requires"
    assert normalize_type("consequence") == "affects"
    assert normalize_type("co_occurring") == "co_occurs_with"
    assert normalize_type("constrains") == "constrains"
    assert normalize_type("requires") == "requires"
    assert normalize_type("enables") is None


# ---------------------------------------------------------------- validation of one new relation


def test_relation_problem_accepts_a_valid_relation():
    dims = _dims(("1", B, []), ("2", A, []))
    assert relation_problem(dims, "1", "2", "requires", render_reading(B, "requires", A)) is None


@pytest.mark.parametrize("source,target,rtype,why", [
    ("1", "1", "requires", "two different"),
    ("1", "9", "requires", "unknown"),
    ("1", "2", "enables", "type"),
    ("1", "2", "refines", "type"),  # not enabled by default
])
def test_relation_problem_basic_rejections(source, target, rtype, why):
    dims = _dims(("1", B, []), ("2", A, []))
    problem = relation_problem(dims, source, target, rtype, "x", check=False)
    assert problem and why in problem


def test_relation_problem_rejects_opposite_pair_cycle_duplicate_and_cap():
    req = lambda t: {"target_id": t, "type": "requires", "reading": "", "rationale": ""}
    dims = _dims(("1", "One", [req("2")]), ("2", "Two", [req("3")]), ("3", "Three", []), ("4", "Four", []))
    assert "opposite" in relation_problem(dims, "2", "1", "requires", "", check=False)
    assert "cycle" in relation_problem(dims, "3", "1", "requires", "", check=False)
    assert "already" in relation_problem(dims, "1", "2", "requires", "", check=False)
    # co_occurs_with is one relation per pair, whichever side it is stored on
    dims[3]["relations"].append({"target_id": "1", "type": "co_occurs_with", "reading": "", "rationale": ""})
    assert "already" in relation_problem(dims, "1", "4", "co_occurs_with", "", check=False)
    capped = relation_problem(dims, "1", "3", "affects", "", check=False, max_per_dimension=1)
    assert capped and "at most 1" in capped


def test_relation_problem_reports_the_canonical_sentence_on_a_bad_reading():
    dims = _dims(("1", B, []), ("2", A, []))
    problem = relation_problem(dims, "1", "2", "requires", render_reading(A, "requires", B))
    assert problem and render_reading(B, "requires", A) in problem


# ---------------------------------------------------------------- clean-up of a whole taxonomy


def test_clean_relations_maps_legacy_drops_invalid_and_normalizes_co_occurrence():
    dims = _dims(
        ("1", "One", [{"target_id": "2", "type": "precondition", "rationale": "r"},
                      {"target_id": "1", "type": "constrains", "rationale": "self"},
                      {"target_id": "9", "type": "constrains", "rationale": "dangling"},
                      {"target_id": "2", "type": "enables", "rationale": "unknown"}]),
        ("2", "Two", [{"target_id": "1", "type": "precondition", "rationale": "opposite"},
                      {"target_id": "1", "type": "co_occurring", "rationale": "co"}]),
    )
    cleaned, dropped = clean_relations(dims)
    one, two = cleaned
    assert [r["type"] for r in one["relations"]] == ["requires", "co_occurs_with"]
    assert two["relations"] == []
    co = one["relations"][1]
    assert co["target_id"] == "2" and co["reading"] == render_reading("One", "co_occurs_with", "Two")
    assert one["relations"][0]["reading"] == render_reading("One", "requires", "Two")
    assert len(dropped) == 4
    assert dims[0]["relations"][0]["type"] == "precondition"  # input untouched


def test_clean_relations_with_checks_drops_bad_readings_and_applies_the_cap():
    good = {"target_id": "2", "type": "requires", "reading": render_reading("One", "requires", "Two"), "rationale": ""}
    bad = {"target_id": "3", "type": "requires", "reading": render_reading("Three", "requires", "One"),
           "rationale": ""}
    extra = {"target_id": "3", "type": "affects", "reading": render_reading("One", "affects", "Three"),
             "rationale": ""}
    dims = _dims(("1", "One", [good, bad, extra]), ("2", "Two", []), ("3", "Three", []))
    cleaned, dropped = clean_relations(dims, check=True, max_per_dimension=1)
    assert cleaned[0]["relations"] == [good]
    assert len(dropped) == 2


def test_relation_sentence_maps_legacy_types_and_falls_back_for_unknown_ones():
    from taxonomy_generator.relations import relation_sentence
    assert relation_sentence({"type": "precondition"}, "Serving", "Packaging") == \
        "Serving requires Packaging to be decided first"
    assert relation_sentence({"type": "enables"}, "Serving", "Packaging") == "Serving enables Packaging"
