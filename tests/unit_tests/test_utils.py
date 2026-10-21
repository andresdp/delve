"""Tests for taxonomy_generator.utils helpers."""

from taxonomy_generator.utils import format_open_codes_for_docs


def test_format_open_codes_for_docs_carries_status_through():
    """The axial-coding data_json must include each code's status — it is
    the field taxonomy_generation.md/taxonomy_update.md instruct the model
    to read when deciding whether codes share a value's axis position."""
    docs = [{"id": "d1", "summary": "s1", "content": "c1"}]
    open_codes = [
        {"doc_id": "d1", "label": "Adopted Redis caching", "rationale": "r1", "status": "accepted"},
        {"doc_id": "d1", "label": "Considered and declined GraphQL", "rationale": "r2", "status": "rejected"},
    ]

    result = format_open_codes_for_docs(docs, open_codes)

    assert '"status": "accepted"' in result
    assert '"status": "rejected"' in result


def test_format_open_codes_for_docs_defaults_status_for_legacy_codes_missing_it():
    """A code dict with no status key (shouldn't occur post-fix, but the
    formatter must not KeyError on it) defaults to accepted."""
    docs = [{"id": "d1", "summary": "s1", "content": "c1"}]
    open_codes = [{"doc_id": "d1", "label": "Some code", "rationale": "r1"}]

    result = format_open_codes_for_docs(docs, open_codes)

    assert '"status": "accepted"' in result


def test_format_open_codes_for_docs_fallback_summary_entry_carries_status():
    """A document with zero open codes falls back to a summary-only code
    entry — that synthetic entry must also carry a status key so every
    entry in the codes array has a uniform shape."""
    docs = [{"id": "d1", "summary": "s1", "content": "c1"}]

    result = format_open_codes_for_docs(docs, open_codes=[])

    assert '"status": "accepted"' in result
    assert "No open codes extracted" in result
