"""Prompt templates loaded from external Markdown files.

System prompts are stored as ``.md`` files alongside this module.
Human messages are defined inline since they are short and stable.
"""

from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

_PROMPTS_DIR = Path(__file__).parent


def _load_prompt(system_file: str, human_msg: str) -> ChatPromptTemplate:
    """Load a system prompt from a Markdown file and pair it with a human message.

    Args:
        system_file: Filename of the ``.md`` file inside the prompts directory.
        human_msg: The human message template string.

    Returns:
        A ``ChatPromptTemplate`` with the loaded system and human messages.
    """
    system_text = (_PROMPTS_DIR / system_file).read_text().strip()
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_text),
            ("human", human_msg),
        ]
    )


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

SUMMARY_GENERATION_PROMPT = _load_prompt(
    "summary_generation.md",
    "Summarize the following text:\n\n{content}",
)

# ---------------------------------------------------------------------------
# Taxonomy generation
# ---------------------------------------------------------------------------

TAXONOMY_GENERATION_PROMPT = _load_prompt(
    "taxonomy_generation.md",
    (
        "# Questions\n"
        "\n"
        "## Q1. Please generate a cluster table from the input data that meets the requirements.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback in your clustering\n"
        "- If user feedback was provided, explicitly explain how you've incorporated their specific concerns and suggestions\n"
        "\n"
        "- The cluster table should be a **flat list** of **mutually exclusive** categories. Sort them based on their semantic relatedness.\n"
        "\n"
        "- Generate as many distinct, well-supported categories as the data warrants — up to **{max_num_clusters}** categories max. If fewer categories better represent the data, prefer quality over quantity.\n"
        "\n"
        "- **Maximize diversity**: Capture the full breadth of themes in the data. Avoid grouping distinct topics into a single broad category.\n"
        "\n"
        "- Be **specific** about each category. **Do not include vague categories** such as \"Other\", \"General\", \"Unclear\", \"Miscellaneous\" or \"Undefined\" in the cluster table.\n"
        "\n"
        "- Every category must serve the stated **use case**. Exclude categories that are not relevant, even if present in the data.\n"
        "\n"
        "- You can ignore low quality or ambiguous data points.\n"
        "\n"
        "## Q2. Why did you cluster the data the way you did? Explain your reasoning **within {explanation_length} words**. Include how you addressed any user feedback."
    ),
)

# ---------------------------------------------------------------------------
# Taxonomy update
# ---------------------------------------------------------------------------

TAXONOMY_UPDATE_PROMPT = _load_prompt(
    "taxonomy_update.md",
    (
        "# Questions\n"
        "\n"
        "## Q1. Update the existing taxonomy based on the new batch of data.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback.\n"
        "\n"
        "- **Preserve what works**: Keep existing categories that remain relevant. Only change what the new data clearly justifies.\n"
        "\n"
        "- **Do not overfit**: The updated taxonomy must represent ALL data seen so far, not just this batch.\n"
        "\n"
        "- You may **add** new categories for themes not covered, **split** broad categories, **merge** overlapping ones, or **rename/refine** for clarity.\n"
        "\n"
        "- **Max {max_num_clusters} categories** total. If already at the limit, consider merging before adding.\n"
        "\n"
        "- If an **\"Other\"** or catch-all category exists, try to minimize it by re-assigning documents to specific categories or creating new specific ones.\n"
        "\n"
        "## Q2. What did you change and why? Explain your reasoning **within {explanation_length} words**. List each modification and its justification."
    ),
)

# ---------------------------------------------------------------------------
# Taxonomy review
# ---------------------------------------------------------------------------

TAXONOMY_REVIEW_PROMPT = _load_prompt(
    "taxonomy_review.md",
    (
        "# Questions\n"
        "\n"
        "## Q1. Review the taxonomy against the review criteria. Make adjustments only where a clear quality issue is identified.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback.\n"
        "\n"
        "- **Minimal intervention**: Only change what is clearly broken or ambiguous. If the taxonomy is well-structured, return it as-is.\n"
        "\n"
        "- **Do not overfit**: The review sample is small. Do not create categories just for edge cases in the sample.\n"
        "\n"
        "- You may **merge** overlapping categories, **split** overly broad ones, **rename** for clarity, or **refine descriptions** for labeling accuracy.\n"
        "\n"
        "- **Max {max_num_clusters} categories** total.\n"
        "\n"
        "- If an **\"Other\"** or catch-all category exists, try to eliminate it by re-assigning its documents to more specific categories.\n"
        "\n"
        "## Q2. What changes did you make (if any) and why? Explain your reasoning **within {explanation_length} words**. If you made no changes, explain why the taxonomy is already adequate."
    ),
)

# ---------------------------------------------------------------------------
# Document labeling
# ---------------------------------------------------------------------------

LABELER_PROMPT = _load_prompt(
    "labeler.md",
    "Classify the following document into the best-fitting category from the taxonomy above.\n\n{content}",
)

__all__ = [
    "SUMMARY_GENERATION_PROMPT",
    "TAXONOMY_GENERATION_PROMPT",
    "TAXONOMY_UPDATE_PROMPT",
    "TAXONOMY_REVIEW_PROMPT",
    "LABELER_PROMPT",
]