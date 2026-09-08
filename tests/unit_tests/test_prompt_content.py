"""Static-rendering tests for prompt template content (Plan U2+).

These tests render prompt templates with sample variables and assert on the
rendered text, without making any live LLM calls. One test function per
prompt template — append new ones here as later units add prompt content.
"""

from taxonomy_generator.prompts import OPEN_CODING_PROMPT


def test_open_coding_prompt_documents_decision_status():
    messages = OPEN_CODING_PROMPT.format_messages(
        use_case="test use case",
        doc_id="d1",
        content="test content",
    )
    system_text = messages[0].content

    assert "accepted" in system_text
    assert "rejected" in system_text
    assert "outcome" in system_text

    # Authoritative-status instruction: status governs downstream
    # filtering/merging, rationale must not contradict it.
    lowered = system_text.lower()
    assert "authoritative" in lowered
