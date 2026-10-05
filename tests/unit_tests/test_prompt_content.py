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

    # Value/code labels must be noun phrases, not status-prefixed sentences.
    assert "noun phrase" in lowered
    assert "rejected: " in lowered


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

    # Value labels must be noun phrases, never status-prefixed sentences.
    assert "noun phrase" in lowered
    assert "never prefix a label with its status" in lowered


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
    assert "Candidate-decision coverage" in system_text
    assert "count as clearly broken" in system_text
    assert "Merge single-candidate dimensions" in system_text
    assert "Merge only when both dimensions ask *the same* question" in system_text

    # R3: preserve each existing value's status verbatim unless a review
    # adjustment genuinely reclassifies it — never silently default to
    # "accepted" on re-emission.
    lowered = system_text.lower()
    assert "status" in lowered
    assert "preserved verbatim" in lowered
    assert "never let the field silently default to `accepted`" in lowered

    # New Review Criteria row for tradeoff/alternative-shaped naming.
    assert "Tradeoff/alternative-shaped naming" in system_text

    # R-value-label: new criterion, allowed adjustment, and preservation rule
    # for value-label noun-phrase style / no status-prefix.
    assert "Value-label phrasing" in system_text
    assert "Relabel value" in system_text
    assert "must be preserved verbatim unless a review adjustment relabels it" in lowered


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

    # Value labels must be noun phrases, never status-prefixed sentences.
    assert "noun phrase" in lowered
    assert "never prefix a label with its status" in lowered


# ---------------------------------------------------------------- tool-based updates (edit_mode: tools)

_TOOLS_VARS = dict(use_case="u", feedback="f", taxonomy_json="[1] A — q", data_json="[]", suggestion_length=30,
                   cluster_name_length=7, cluster_description_length=23, explanation_length=40,
                   max_num_clusters="9")


def _system(prompt):
    return prompt.format_messages(**_TOOLS_VARS)[0].content


def test_rewrite_prompts_are_the_files_verbatim():
    from pathlib import Path

    import taxonomy_generator.prompts as prompts

    folder = Path(prompts.__file__).parent
    for prompt, name in ((TAXONOMY_UPDATE_PROMPT, "taxonomy_update.md"), (TAXONOMY_REVIEW_PROMPT, "taxonomy_review.md")):
        assert prompt.messages[0].prompt.template == (folder / name).read_text().strip()


def test_tools_prompts_keep_the_framework_and_drop_the_output_instructions():
    from taxonomy_generator.prompts import (
        TAXONOMY_REVIEW_TOOLS_PROMPT,
        TAXONOMY_UPDATE_TOOLS_PROMPT,
    )

    for prompt in (TAXONOMY_UPDATE_TOOLS_PROMPT, TAXONOMY_REVIEW_TOOLS_PROMPT):
        text = _system(prompt)
        assert "## Design Space Framework" in text
        assert "### User Feedback Integration" in text
        assert "### Format" not in text
        assert "Carry the taxonomy forward" not in text
        assert "Existing values are shown without their document ids" not in text
        assert "### Tools" in text and "finish" in text and "add_evidence" in text
        # non-output rules of the removed Format section, restated with their values
        assert "7 words" in text and "23 words" in text and "9" in text
        assert "same status" in text
    assert "Dimension-Oriented Operations" in _system(TAXONOMY_UPDATE_TOOLS_PROMPT)
    assert "Allowed Adjustments" in _system(TAXONOMY_REVIEW_TOOLS_PROMPT)
    assert "keep each value's status and label" in _system(TAXONOMY_REVIEW_TOOLS_PROMPT)


def test_tools_human_messages_ask_for_tool_calls():
    from taxonomy_generator.prompts import TAXONOMY_UPDATE_TOOLS_PROMPT

    human = TAXONOMY_UPDATE_TOOLS_PROMPT.format_messages(**_TOOLS_VARS)[1].content
    assert "tools" in human and "finish" in human and "40 words" in human


def test_tools_variant_fails_loudly_when_a_marker_is_missing():
    import pytest

    from taxonomy_generator.prompts import derive_tools_system_prompt

    with pytest.raises(ValueError, match="### Format"):
        derive_tools_system_prompt("# Instruction\n- **Carry the taxonomy forward.** x\n"
                                   "- **Existing values are shown without their document ids**: y\n", "TOOLS")
    with pytest.raises(ValueError, match="Carry the taxonomy forward"):
        derive_tools_system_prompt("# Instruction\n### Format\n- a\n### Quality\n- b\n", "TOOLS")


def test_tools_prompts_ask_for_options_not_codes():
    from taxonomy_generator.prompts import (
        TAXONOMY_REVIEW_TOOLS_PROMPT,
        TAXONOMY_UPDATE_TOOLS_PROMPT,
    )

    for prompt in (TAXONOMY_UPDATE_TOOLS_PROMPT, TAXONOMY_REVIEW_TOOLS_PROMPT):
        text = _system(prompt)
        assert "Values are design options, not codes" in text
        assert "constant comparison" in text
        assert "instance or variant" in text and "merge_values" in text
