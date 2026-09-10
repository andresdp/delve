"""Static-rendering tests for prompt template content (Plan U2+).

These tests render prompt templates with sample variables and assert on the
rendered text, without making any live LLM calls. One test function per
prompt template — append new ones here as later units add prompt content.
"""

from taxonomy_generator.prompts import (
    OPEN_CODING_PROMPT,
    TAXONOMY_GENERATION_PROMPT,
    TAXONOMY_REVIEW_PROMPT,
    TAXONOMY_UPDATE_PROMPT,
)


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


def test_taxonomy_generation_prompt_anchors_quality_attributes_and_status():
    messages = TAXONOMY_GENERATION_PROMPT.format_messages(
        use_case="test use case",
        feedback="no feedback",
        cluster_name_length="5",
        cluster_description_length="20",
        explanation_length="200",
        max_num_clusters="10",
        data_json="[]",
    )
    system_text = messages[0].content

    # R7: quality-attribute anchoring before finalizing dimensions.
    assert "quality attributes" in system_text

    # R3: a value's supporting codes must share one status — no merging
    # codes/values of different status into one Value.
    lowered = system_text.lower()
    assert "status" in lowered
    assert "never group codes of different status into one value" in lowered

    # A dimension must name an axis, not a tradeoff or alternative-set.
    assert "tradeoff" in lowered
    assert "alternative" in lowered
    assert "relations" in lowered


def test_taxonomy_review_prompt_has_new_criteria_and_status_preservation():
    messages = TAXONOMY_REVIEW_PROMPT.format_messages(
        use_case="test use case",
        feedback="no feedback",
        cluster_name_length="5",
        cluster_description_length="20",
        explanation_length="200",
        max_num_clusters="10",
        data_json="[]",
        taxonomy_json="[]",
    )
    system_text = messages[0].content

    # R8/R10: new Review Criteria rows.
    assert "Quality-attribute grounding" in system_text
    assert "Rejected-alternative handling" in system_text
    assert "Design-space gap awareness" in system_text

    # R3: preserve each existing value's status verbatim unless a review
    # adjustment genuinely reclassifies it — never silently default to
    # "accepted" on re-emission.
    lowered = system_text.lower()
    assert "status" in lowered
    assert "preserved verbatim" in lowered
    assert "never let the field silently default to `accepted`" in lowered

    # New Review Criteria row for tradeoff/alternative-shaped naming.
    assert "Tradeoff/alternative-shaped naming" in system_text


def test_taxonomy_update_prompt_anchors_quality_attributes_and_status():
    messages = TAXONOMY_UPDATE_PROMPT.format_messages(
        use_case="test use case",
        feedback="no feedback",
        cluster_name_length="5",
        cluster_description_length="20",
        explanation_length="200",
        max_num_clusters="10",
        data_json="[]",
        taxonomy_json="[]",
    )
    system_text = messages[0].content

    # R7: quality-attribute anchoring before finalizing dimensions.
    assert "quality attributes" in system_text

    # R3: a value's supporting codes must share one status — no merging
    # codes/values of different status into one Value.
    lowered = system_text.lower()
    assert "status" in lowered
    assert "never group codes of different status into one value" in lowered

    # A dimension must name an axis, not a tradeoff or alternative-set.
    assert "tradeoff" in lowered
    assert "alternative" in lowered
    assert "relations" in lowered
