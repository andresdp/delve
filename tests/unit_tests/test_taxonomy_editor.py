"""TaxonomyEditor: validated coding operations on a stored taxonomy — no LLM calls."""

import copy

import pytest

from taxonomy_generator.taxonomy_editor import TaxonomyEditor


def _taxonomy():
    return [
        {"id": "1", "name": "Drift Test", "description": "Which test detects drift?",
         "relations": [{"target_id": "2", "type": "consequence", "rationale": "alerts trigger responses"}],
         "values": [
             {"id": "1.1", "dimension_id": "1", "label": "CUSUM chart", "description": "cumulative sums",
              "supporting_doc_ids": ["d1"], "status": "accepted"},
             {"id": "1.2", "dimension_id": "1", "label": "KS test", "description": "distribution test",
              "supporting_doc_ids": ["d2"], "status": "rejected"},
             {"id": "1.3", "dimension_id": "1", "label": "Mean shift test", "description": "compare means",
              "supporting_doc_ids": [], "status": "accepted"},
             {"id": "1.4", "dimension_id": "1", "label": "Faster alerts", "description": "an effect",
              "supporting_doc_ids": ["d1"], "status": "outcome"},
         ]},
        {"id": "2", "name": "Response Strategy", "description": "How to respond to alerts?", "relations": [],
         "values": [
             {"id": "2.1", "dimension_id": "2", "label": "Rollback", "description": "revert",
              "supporting_doc_ids": ["d3"], "status": "accepted"},
             {"id": "2.2", "dimension_id": "2", "label": "Human review", "description": "escalate",
              "supporting_doc_ids": ["d3"], "status": "accepted"},
         ]},
        {"id": "3", "name": "Empty Dim", "description": "nothing yet", "relations": [], "values": []},
    ]


def _editor(review=False, batch=("d1", "d2", "d4", "d5")):
    return TaxonomyEditor(_taxonomy(), batch_doc_ids=batch, review=review)


def _dim(clusters, dim_id):
    return next(c for c in clusters if c["id"] == dim_id)


def _value(clusters, value_id):
    return next(v for c in clusters for v in c["values"] if v["id"] == value_id)


def _labels(clusters):
    return {v["label"] for c in clusters for v in c["values"]}


# ---------------------------------------------------------------- values


def test_add_value_creates_next_id_with_documents_and_logs_it():
    ed = _editor()
    ok, msg = ed.apply("add_value", {"dimension_id": "1", "label": "Page-Hinkley test", "description": "change point",
                                     "status": "accepted", "doc_ids": ["d4"], "reason": "new code in d4"})
    assert ok, msg
    assert "1.5" in msg
    v = _value(ed.clusters, "1.5")
    assert v["label"] == "Page-Hinkley test" and v["supporting_doc_ids"] == ["d4"] and v["dimension_id"] == "1"
    assert ed.operations[-1]["tool"] == "add_value"


def test_add_value_duplicate_label_same_status_is_rejected_with_add_evidence_hint():
    ed = _editor()
    before = copy.deepcopy(ed.clusters)
    ok, msg = ed.apply("add_value", {"dimension_id": "1", "label": "cusum  Chart", "description": "x",
                                     "status": "accepted", "doc_ids": ["d4"], "reason": "r"})
    assert not ok and "add_evidence" in msg
    assert ed.clusters == before
    assert ed.rejected[-1]["tool"] == "add_value"


def test_add_value_same_label_different_status_is_allowed():
    ed = _editor()
    ok, msg = ed.apply("add_value", {"dimension_id": "1", "label": "CUSUM chart", "description": "declined here",
                                     "status": "rejected", "doc_ids": ["d4"], "reason": "d4 rejects it"})
    assert ok, msg


def test_add_value_with_document_outside_the_batch_is_rejected():
    ed = _editor()
    before = copy.deepcopy(ed.clusters)
    ok, msg = ed.apply("add_value", {"dimension_id": "1", "label": "New", "description": "x", "status": "accepted",
                                     "doc_ids": ["d9"], "reason": "r"})
    assert not ok and "d9" in msg
    assert ed.clusters == before


@pytest.mark.parametrize("args, fragment", [
    ({"dimension_id": "9", "label": "New", "description": "x", "status": "accepted", "doc_ids": ["d4"]}, "dimension"),
    ({"dimension_id": "1", "label": "New", "description": "x", "status": "mixed", "doc_ids": ["d4"]}, "status"),
    ({"dimension_id": "1", "label": "New", "description": "x", "status": "accepted", "doc_ids": []}, "doc_ids"),
    ({"dimension_id": "1", "description": "x", "status": "accepted", "doc_ids": ["d4"]}, "label"),
])
def test_add_value_validation_errors(args, fragment):
    ok, msg = _editor().apply("add_value", {**args, "reason": "r"})
    assert not ok and fragment in msg


def test_add_evidence_unions_documents_without_duplicates():
    ed = _editor()
    ok, msg = ed.apply("add_evidence", {"value_id": "1.1", "doc_ids": ["d1", "d4", "d4"], "reason": "r"})
    assert ok, msg
    assert _value(ed.clusters, "1.1")["supporting_doc_ids"] == ["d1", "d4"]


def test_move_value_then_add_evidence_with_old_id_resolves_alias():
    ed = _editor()
    ok, msg = ed.apply("move_value", {"value_id": "1.3", "to_dimension_id": "2", "reason": "answers question 2"})
    assert ok, msg
    moved = next(v for v in _dim(ed.clusters, "2")["values"] if v["label"] == "Mean shift test")
    assert moved["id"] == "2.3" and moved["dimension_id"] == "2"
    assert all(v["label"] != "Mean shift test" for v in _dim(ed.clusters, "1")["values"])
    ok, msg = ed.apply("add_evidence", {"value_id": "1.3", "doc_ids": ["d5"], "reason": "r"})
    assert ok, msg
    assert moved["supporting_doc_ids"] == ["d5"]


def test_move_value_to_same_dimension_is_rejected():
    ok, msg = _editor().apply("move_value", {"value_id": "1.1", "to_dimension_id": "1", "reason": "r"})
    assert not ok


def test_merge_values_with_different_status_is_rejected():
    ed = _editor()
    for ids in (["1.1", "1.2"], ["1.1", "1.4"]):
        ok, msg = ed.apply("merge_values", {"value_ids": ids, "label": "X", "description": "x", "reason": "r"})
        assert not ok and "status" in msg


def test_merge_values_same_status_unions_documents_and_records_merged_from():
    ed = _editor()
    ok, msg = ed.apply("merge_values", {"value_ids": ["1.1", "1.3"], "label": "Sequential change test",
                                        "description": "cusum family", "reason": "same option"})
    assert ok, msg
    merged = _value(ed.clusters, "1.1")
    assert merged["label"] == "Sequential change test" and merged["status"] == "accepted"
    assert merged["supporting_doc_ids"] == ["d1"]
    assert merged["merged_from"] == [{"id": "1.3", "label": "Mean shift test"}]
    assert all(v["id"] != "1.3" for v in _dim(ed.clusters, "1")["values"])
    ok, _ = ed.apply("add_evidence", {"value_id": "1.3", "doc_ids": ["d4"], "reason": "alias"})
    assert ok and merged["supporting_doc_ids"] == ["d1", "d4"]


def test_merge_values_across_dimensions_is_rejected():
    ok, msg = _editor().apply("merge_values", {"value_ids": ["1.1", "2.1"], "label": "X", "description": "x",
                                               "reason": "r"})
    assert not ok and "dimension" in msg


def test_relabel_value_rejects_duplicate_label():
    ed = _editor()
    ok, msg = ed.apply("relabel_value", {"value_id": "1.3", "label": "CUSUM chart", "reason": "r"})
    assert not ok
    ok, msg = ed.apply("relabel_value", {"value_id": "1.3", "label": "Mean-shift test", "description": "new",
                                         "reason": "r"})
    assert ok and _value(ed.clusters, "1.3")["description"] == "new"


def test_set_status_outside_review_needs_a_batch_document_in_reason():
    ed = _editor()
    ok, msg = ed.apply("set_status", {"value_id": "1.3", "status": "rejected", "reason": "seems declined"})
    assert not ok and "document" in msg
    ok, msg = ed.apply("set_status", {"value_id": "1.3", "status": "rejected", "reason": "d4 declines it"})
    assert ok and _value(ed.clusters, "1.3")["status"] == "rejected"


def test_set_status_in_review_needs_no_document():
    ed = _editor(review=True)
    ok, msg = ed.apply("set_status", {"value_id": "1.3", "status": "rejected", "reason": "sample shows it"})
    assert ok, msg


def test_remove_value_blocked_when_supported_allowed_when_not():
    ed = _editor()
    ok, msg = ed.apply("remove_value", {"value_id": "1.1", "reason": "r"})
    assert not ok and "supporting" in msg
    ok, msg = ed.apply("remove_value", {"value_id": "1.3", "reason": "no evidence"})
    assert ok and "Mean shift test" not in _labels(ed.clusters)


# ---------------------------------------------------------------- dimensions


def test_add_dimension_returns_new_id_and_rejects_duplicate_name():
    ed = _editor()
    ok, msg = ed.apply("add_dimension", {"name": "Alert Threshold", "description": "how alerts fire", "reason": "r"})
    assert ok and "4" in msg
    ok, msg = ed.apply("add_dimension", {"name": "drift test", "description": "dup", "reason": "r"})
    assert not ok


def test_rename_dimension():
    ed = _editor()
    ok, msg = ed.apply("rename_dimension", {"dimension_id": "2", "name": "Response Action", "reason": "r"})
    assert ok and _dim(ed.clusters, "2")["name"] == "Response Action"
    ok, msg = ed.apply("rename_dimension", {"dimension_id": "2", "name": "Drift Test", "reason": "r"})
    assert not ok


def test_split_dimension_assigns_every_value_once_and_copies_relations():
    ed = _editor()
    ed.apply("add_value", {"dimension_id": "1", "label": "Page-Hinkley", "description": "x", "status": "rejected",
                           "doc_ids": ["d4"], "reason": "r"})
    ok, msg = ed.apply("split_dimension", {"dimension_id": "1", "reason": "two questions", "parts": [
        {"name": "Sequential Test", "description": "a", "value_ids": ["1.1", "1.5", "1.4"]},
        {"name": "Distribution Test", "description": "b", "value_ids": ["1.2", "1.3"]}]})
    assert ok, msg
    names = {c["name"] for c in ed.clusters}
    assert {"Sequential Test", "Distribution Test"} <= names and "Drift Test" not in names
    for part in ("Sequential Test", "Distribution Test"):
        dim = next(c for c in ed.clusters if c["name"] == part)
        assert dim["relations"] == [{"target_id": "2", "type": "consequence", "rationale": "alerts trigger responses"}]
        assert all(v["dimension_id"] == dim["id"] for v in dim["values"])
    assert len([v for c in ed.clusters for v in c["values"]]) == 7
    ok, _ = ed.apply("add_evidence", {"value_id": "1.2", "doc_ids": ["d5"], "reason": "alias"})
    assert ok


def test_split_dimension_leaving_a_single_candidate_is_rejected():
    ed = _editor()
    ok, msg = ed.apply("split_dimension", {"dimension_id": "1", "reason": "r", "parts": [
        {"name": "A", "description": "a", "value_ids": ["1.1", "1.2", "1.4"]},
        {"name": "B", "description": "b", "value_ids": ["1.3"]}]})
    assert not ok and "move" in msg


@pytest.mark.parametrize("parts", [
    [{"name": "A", "description": "a", "value_ids": ["1.1", "1.2"]},
     {"name": "B", "description": "b", "value_ids": ["1.3"]}],                       # 1.4 missing
    [{"name": "A", "description": "a", "value_ids": ["1.1", "1.2", "1.4"]},
     {"name": "B", "description": "b", "value_ids": ["1.3", "1.1"]}],                # 1.1 twice
    [{"name": "A", "description": "a", "value_ids": ["1.1", "1.2", "1.3", "1.4"]}],  # one part
])
def test_split_dimension_must_cover_each_value_exactly_once(parts):
    ed = _editor()
    before = copy.deepcopy(ed.clusters)
    ok, _ = ed.apply("split_dimension", {"dimension_id": "1", "parts": parts, "reason": "r"})
    assert not ok and ed.clusters == before


def test_merge_dimensions_combines_values_and_deduplicates_relations():
    ed = _editor()
    ed.apply("add_relation", {"source_id": "2", "target_id": "3", "type": "co_occurring", "rationale": "x"})
    ed.apply("add_value", {"dimension_id": "3", "label": "Rollback", "description": "dup label elsewhere",
                           "status": "accepted", "doc_ids": ["d4"], "reason": "r"})
    ok, msg = ed.apply("merge_dimensions", {"dimension_ids": ["2", "3"], "name": "Response", "description": "d",
                                            "reason": "both ask how to respond"})
    assert ok, msg
    merged = _dim(ed.clusters, "2")
    assert merged["name"] == "Response"
    assert [v["label"] for v in merged["values"]] == ["Rollback", "Human review", "Rollback"]
    assert all(r["target_id"] != "2" and r["target_id"] != "3" for r in merged["relations"])
    assert all(c["id"] != "3" for c in ed.clusters)
    incoming = _dim(ed.clusters, "1")["relations"]
    assert incoming == [{"target_id": "2", "type": "consequence", "rationale": "alerts trigger responses"}]


def test_merge_dimensions_needs_a_reason():
    ok, msg = _editor().apply("merge_dimensions", {"dimension_ids": ["2", "3"], "name": "R", "description": "d",
                                                   "reason": ""})
    assert not ok and "reason" in msg


def test_remove_dimension_only_when_empty():
    ed = _editor()
    ok, msg = ed.apply("remove_dimension", {"dimension_id": "2", "reason": "r"})
    assert not ok and "values" in msg
    ok, msg = ed.apply("remove_dimension", {"dimension_id": "3", "reason": "unused"})
    assert ok and all(c["id"] != "3" for c in ed.clusters)


# ---------------------------------------------------------------- relations and control


def test_add_relation_validates_type_and_duplicates():
    ed = _editor()
    ok, msg = ed.apply("add_relation", {"source_id": "1", "target_id": "2", "type": "enables", "rationale": "x"})
    assert not ok and "type" in msg
    ok, msg = ed.apply("add_relation", {"source_id": "1", "target_id": "2", "type": "consequence", "rationale": "x"})
    assert not ok and "exists" in msg
    ok, msg = ed.apply("add_relation", {"source_id": "2", "target_id": "1", "type": "constrains", "rationale": "x"})
    assert ok, msg


def test_remove_relation():
    ed = _editor()
    ok, _ = ed.apply("remove_relation", {"source_id": "1", "target_id": "2", "reason": "r"})
    assert ok and _dim(ed.clusters, "1")["relations"] == []
    ok, _ = ed.apply("remove_relation", {"source_id": "1", "target_id": "2", "reason": "r"})
    assert not ok


def test_finish_records_explanation():
    ed = _editor()
    ok, _ = ed.apply("finish", {"explanation": "Added one value."})
    assert ok and ed.finished and ed.explanation == "Added one value."


def test_unknown_tool_and_bad_arguments_are_errors_not_exceptions():
    ed = _editor()
    assert not ed.apply("delete_everything", {})[0]
    assert not ed.apply("add_evidence", {"value_id": "1.1", "doc_ids": "d4"})[0]
    assert not ed.apply("add_evidence", "not a dict")[0]


# ---------------------------------------------------------------- result


def test_result_drops_dangling_relations_and_new_empty_dimensions():
    ed = _editor()
    ed.apply("add_dimension", {"name": "Unused", "description": "x", "reason": "r"})
    ed.apply("remove_value", {"value_id": "1.3", "reason": "r"})
    ed.clusters[1]["relations"].append({"target_id": "99", "type": "constrains", "rationale": "stale"})
    clusters = ed.result()
    assert all(c["name"] != "Unused" for c in clusters)
    assert any(c["name"] == "Empty Dim" for c in clusters)  # pre-existing empty dimension is kept
    assert all(r["target_id"] != "99" for c in clusters for r in c.get("relations", []))
    notes = " ".join(ed.cleanup)
    assert "Unused" in notes and "99" in notes


def test_result_lists_uncited_batch_documents():
    ed = _editor(batch=("d1", "d4", "d5"))
    ed.apply("add_evidence", {"value_id": "1.1", "doc_ids": ["d4"], "reason": "r"})
    ed.result()
    assert ed.uncited == ["d5"]


def test_input_taxonomy_is_not_mutated():
    original = _taxonomy()
    ed = TaxonomyEditor(original, batch_doc_ids=["d4"])
    ed.apply("add_evidence", {"value_id": "1.1", "doc_ids": ["d4"], "reason": "r"})
    ed.apply("rename_dimension", {"dimension_id": "1", "name": "Renamed", "reason": "r"})
    assert original == _taxonomy()


def test_no_value_is_lost_without_a_logged_removal():
    """Property: after valid non-removal operations every previous value id (or alias) resolves."""
    ed = _editor()
    previous = [v["id"] for c in _taxonomy() for v in c["values"]]
    ed.apply("move_value", {"value_id": "1.3", "to_dimension_id": "3", "reason": "r"})
    ed.apply("merge_values", {"value_ids": ["2.1", "2.2"], "label": "Act", "description": "x", "reason": "r"})
    ed.apply("add_dimension", {"name": "New", "description": "x", "reason": "r"})
    ed.apply("merge_dimensions", {"dimension_ids": ["2", "3"], "name": "Resp", "description": "x", "reason": "same q"})
    current = {v["id"] for c in ed.clusters for v in c["values"]}
    for vid in previous:
        assert ed.resolve_value(vid) in current
