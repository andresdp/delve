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
