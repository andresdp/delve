"""Summarization keeps each document's id and content (passage ids such as s03_p02 must survive)."""

from taxonomy_generator.nodes.summary_generator import _as_documents
from taxonomy_generator.state import Doc


def test_doc_objects_keep_their_id_and_content():
    docs = _as_documents([Doc(id="s03_p02", content="Spokes keeps three replicas.")])
    assert docs == [{"id": "s03_p02", "content": "Spokes keeps three replicas."}]


def test_dicts_and_strings_are_kept_or_given_an_id():
    docs = _as_documents([{"id": "s01_p01", "content": "a"}, {"content": "b"}, "c"])
    assert docs[0] == {"id": "s01_p01", "content": "a"}
    assert docs[1]["content"] == "b" and docs[1]["id"]
    assert docs[2]["content"] == "c" and docs[2]["id"]
