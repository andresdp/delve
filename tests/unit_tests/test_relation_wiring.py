"""Relation rules applied where taxonomies enter or change outside the editor: rewrite output and dimension merging."""

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.nodes.dimension_merger import merge_groups
from taxonomy_generator.relations import render_reading
from taxonomy_generator.utils import sanitize_relations


def _dims(*specs):
    return [{"id": i, "name": n, "description": "", "relations": list(r), "values": []} for i, n, r in specs]


def test_rewrite_output_keeps_well_read_relations_and_drops_the_rest():
    good = {"target_id": "2", "type": "requires", "reading": "Serving requires Packaging to be decided first",
            "rationale": "r"}
    reversed_ = {"target_id": "3", "type": "requires", "reading": "Monitoring requires Serving to be decided first",
                 "rationale": "r"}
    disabled = {"target_id": "3", "type": "refines", "reading": "Serving is a sub-decision of Monitoring",
                "rationale": "r"}
    clusters = _dims(("1", "Serving", [good, reversed_, disabled]), ("2", "Packaging", []), ("3", "Monitoring", []))
    config = Configuration(relation_types=("requires", "affects", "constrains", "co_occurs_with"),
                           max_relations_per_dimension=3)
    cleaned, notes = sanitize_relations(clusters, config)
    assert cleaned[0]["relations"] == [good]
    assert len(notes) == 2 and all("dropped relation" in n for n in notes)


def test_rewrite_output_respects_the_cap():
    rels = [{"target_id": t, "type": "affects", "reading": f"Choices on Serving affect the outcomes of {n}",
             "rationale": "r"} for t, n in (("2", "Packaging"), ("3", "Monitoring"))]
    clusters = _dims(("1", "Serving", rels), ("2", "Packaging", []), ("3", "Monitoring", []))
    cleaned, notes = sanitize_relations(clusters, Configuration(max_relations_per_dimension=1))
    assert [r["target_id"] for r in cleaned[0]["relations"]] == ["2"] and len(notes) == 1


def test_dimension_merging_drops_relations_that_become_opposite():
    dims = _dims(("1", "Serving", [{"target_id": "2", "type": "requires", "rationale": "r"}]),
                 ("2", "Packaging", []),
                 ("3", "Packaging format", [{"target_id": "1", "type": "requires", "rationale": "r"}]))
    merged, notes = merge_groups(dims, [[0], [1, 2]])
    rels = {(c["id"], r["target_id"], r["type"]) for c in merged for r in c["relations"]}
    assert rels == {("1", "2", "requires")}
    assert any("opposite" in n for n in notes)


def test_rewrite_output_keeps_existing_relations_after_a_rename_and_refreshes_their_reading():
    previous = _dims(("1", "Serving", [{"target_id": "2", "type": "requires", "rationale": "r",
                                        "reading": "Serving requires Packaging to be decided first"}]),
                     ("2", "Packaging", []))
    # the model renamed dimension 2 and copied the relation (and its old reading) unchanged
    output = _dims(("1", "Serving", [{"target_id": "2", "type": "requires", "rationale": "r",
                                      "reading": "Serving requires Packaging to be decided first"}]),
                   ("2", "Model Packaging Format", []))
    cleaned, notes = sanitize_relations(output, Configuration(), previous=previous)
    assert notes == []
    assert cleaned[0]["relations"][0]["reading"] == render_reading("Serving", "requires", "Model Packaging Format")


def test_rewrite_output_still_checks_relations_that_are_new():
    previous = _dims(("1", "Serving", []), ("2", "Packaging", []))
    output = _dims(("1", "Serving", [{"target_id": "2", "type": "requires", "rationale": "r",
                                      "reading": "Packaging requires Serving to be decided first"}]),
                   ("2", "Packaging", []))
    cleaned, notes = sanitize_relations(output, Configuration(), previous=previous)
    assert cleaned[0]["relations"] == [] and len(notes) == 1


def test_dimension_merging_applies_the_cap():
    rels = [{"target_id": t, "type": "affects", "rationale": "r"} for t in ("3", "4")]
    dims = _dims(("1", "A", rels[:1]), ("2", "A too", rels[1:]), ("3", "C", []), ("4", "D", []))
    merged, notes = merge_groups(dims, [[0, 1], [2], [3]], max_relations=1)
    assert max(len(c["relations"]) for c in merged) == 1
    assert any("at most 1" in n for n in notes)
