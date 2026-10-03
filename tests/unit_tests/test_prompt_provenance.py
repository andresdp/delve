"""Rewrite prompts hide provenance; kept values get their evidence back; stale feedback is not passed."""

from taxonomy_generator.state import State
from taxonomy_generator.utils import carry_over_evidence, format_feedback, taxonomy_prompt_view

PREVIOUS = [{
    "id": "1", "name": "Drift Detection Test", "description": "",
    "evidence": {"codes": 2}, "merged_from": [],
    "values": [
        {"id": "1.1", "label": "CUSUM test", "status": "accepted", "supporting_doc_ids": ["s01_p01", "s02_p03"],
         "stances": {"accepted": ["s01_p01"]}},
        {"id": "1.2", "label": "KS test", "status": "accepted", "supporting_doc_ids": ["s04_p01"]},
    ],
}]


def test_prompt_view_drops_provenance_but_keeps_structure():
    view = taxonomy_prompt_view(PREVIOUS)
    assert "evidence" not in view[0] and "merged_from" not in view[0]
    assert view[0]["values"][0] == {"id": "1.1", "label": "CUSUM test", "status": "accepted"}
    assert PREVIOUS[0]["values"][0]["supporting_doc_ids"]  # the original is untouched


def test_kept_values_recover_their_documents_by_label_or_by_id():
    updated = [
        {"id": "2", "name": "Change Detection Method", "values": [
            {"id": "2.1", "label": "Cusum Test", "supporting_doc_ids": ["s09_p02"]},  # moved, same label
        ]},
        {"id": "1", "name": "Drift Detection Test", "values": [
            {"id": "1.2", "label": "Kolmogorov-Smirnov test", "supporting_doc_ids": []},  # relabeled in place
            {"id": "1.3", "label": "Page-Hinkley test", "supporting_doc_ids": ["s10_p01"]},  # new
        ]},
    ]
    carry_over_evidence(PREVIOUS, updated)
    assert updated[0]["values"][0]["supporting_doc_ids"] == ["s01_p01", "s02_p03", "s09_p02"]
    assert updated[1]["values"][0]["supporting_doc_ids"] == ["s04_p01"]
    assert updated[1]["values"][1]["supporting_doc_ids"] == ["s10_p01"]


BOARD = {"criteria": [{"name": "Orthogonality", "score": 0.2, "threshold": 0.5, "evaluated": True,
                       "reason": "merge dimensions 2 and 5"}], "overall": 0.2, "unavailable": False}


def test_feedback_uses_only_a_scoreboard_of_the_current_draft():
    drafts = [[{"id": "1"}]] * 3
    current = State(clusters=drafts, evaluation_history=[{**BOARD, "iteration": 3}])
    stale = State(clusters=drafts, evaluation_history=[{**BOARD, "iteration": 1}])
    assert "merge dimensions 2 and 5" in format_feedback(current)
    assert format_feedback(stale) == "None."
