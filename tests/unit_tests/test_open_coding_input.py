"""Open coding input selection (summary vs. full content) and its setting."""

import pytest

from taxonomy_generator.nodes.open_coder import _doc_input
from taxonomy_generator.settings import load_settings
from taxonomy_generator.state import Doc


def test_summary_source_prefers_summary_then_content():
    assert _doc_input(Doc(id="d", content="full text", summary="short")) == "short"
    assert _doc_input(Doc(id="d", content="full text")) == "full text"
    assert _doc_input({"id": "d", "content": "full text", "summary": "short"}) == "short"


def test_content_source_always_codes_full_text():
    assert _doc_input(Doc(id="d", content="full text", summary="short"), "content") == "full text"
    assert _doc_input({"id": "d", "content": "full text", "summary": "short"}, "content") == "full text"
    # Falls back to the summary only when there is no content at all.
    assert _doc_input(Doc(id="d", content="", summary="short"), "content") == "short"


def test_setting_defaults_to_summary_and_accepts_content(tmp_path):
    default = tmp_path / "default.yaml"
    default.write_text("models: {}\n")
    assert load_settings(str(default)).open_coding.input == "summary"

    content = tmp_path / "content.yaml"
    content.write_text("open_coding:\n  input: content\n")
    assert load_settings(str(content)).open_coding.input == "content"


def test_invalid_setting_is_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("open_coding:\n  input: passages\n")
    with pytest.raises(ValueError, match="open_coding.input"):
        load_settings(str(bad))
