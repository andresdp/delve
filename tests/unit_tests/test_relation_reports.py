"""Reports write relations as reading sentences (legacy type names mapped)."""

from taxonomy_generator.report_renderer import render_catalog, render_diagram

DIMS = [
    {"id": "1", "name": "Serving", "description": "", "values": [],
     "relations": [{"target_id": "2", "type": "precondition", "rationale": "packaging first"},
                   {"target_id": "2", "type": "co_occurs_with", "rationale": "together"}]},
    {"id": "2", "name": "Packaging", "description": "", "values": [], "relations": []},
]


def test_catalog_lists_relations_as_sentences():
    text = render_catalog(DIMS)
    assert "Serving requires Packaging to be decided first (#2): packaging first" in text
    assert "precondition" not in text


def test_diagram_labels_use_current_type_names_and_undirected_edges_have_no_arrow():
    text = render_diagram(DIMS)
    assert "-->|requires|" in text
    assert "---|co_occurs_with|" in text


def test_narrative_prompt_dimensions_carry_in_view_relation_sentences_only():
    from taxonomy_generator.report_renderer import _format_dimensions_for_prompt

    dims = [
        {"id": "1", "name": "Serving", "description": "How is the model served?", "values": [],
         "relations": [{"target_id": "2", "type": "precondition", "rationale": "x"},
                       {"target_id": "9", "type": "co_occurs_with", "rationale": "y"}]},
        {"id": "2", "name": "Packaging", "description": "How is it packaged?", "values": [], "relations": []},
    ]
    text = _format_dimensions_for_prompt(dims)
    assert "- Serving: How is the model served?\n  - Serving requires Packaging to be decided first" in text
    assert "co_occurs" not in text and "#9" not in text
    assert text.endswith("- Packaging: How is it packaged?")
