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
        "## Q1. Please generate a taxonomy of orthogonal dimensions from the input data that meets the requirements.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback in your clustering\n"
        "- If user feedback was provided, explicitly explain how you've incorporated their specific concerns and suggestions\n"
        "\n"
        "- Each category is a **dimension** — an axis of variation along which documents differ. Think of the taxonomy as a design space where each dimension captures a fundamentally different *type* of distinction.\n"
        "\n"
        "- The taxonomy should be a **flat list** of **orthogonal dimensions**. Sort them based on their semantic relatedness.\n"
        "\n"
        "- Generate as many distinct, well-supported dimensions as the data warrants — up to **{max_num_clusters}** dimensions max. If fewer dimensions better represent the data, prefer quality over quantity.\n"
        "\n"
        "- **Maximize dimensional coverage**: Capture the full breadth of variation in the data. Each dimension should represent a fundamentally different *kind* of content or purpose.\n"
        "\n"
        "- **Check for axis vs. value confusion**: If two categories are really just different values on the same axis (e.g., \"Minor Bugs\" vs \"Critical Bugs\" are both values of \"Bug Severity\"), merge them into one dimension.\n"
        "\n"
        "- Be **specific** about each dimension. **Do not include vague dimensions** such as \"Other\", \"General\", \"Unclear\", \"Miscellaneous\" or \"Undefined\".\n"
        "\n"
        "- Every dimension must serve the stated **use case**. Exclude dimensions that are not relevant, even if present in the data.\n"
        "\n"
        "- You can ignore low quality or ambiguous data points.\n"
        "\n"
        "## Q2. Why did you choose these dimensions? Explain your reasoning **within {explanation_length} words**. For each dimension, explain what axis of variation it captures and why it is orthogonal to the others. Include how you addressed any user feedback."
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
        "## Q1. Update the existing dimension-oriented taxonomy based on the new batch of data.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback.\n"
        "\n"
        "- **Preserve what works**: Keep existing dimensions that remain relevant. Only change what the new data clearly justifies.\n"
        "\n"
        "- **Do not overfit**: The updated taxonomy must represent ALL data seen so far, not just this batch.\n"
        "\n"
        "- You may **add** new dimensions for unseen axes of variation, **split** dimensions that conflate different axes, **merge** dimensions that are really values on the same axis, or **rename/refine** for clarity.\n"
        "\n"
        "- **Max {max_num_clusters} dimensions** total. If already at the limit, consider merging before adding.\n"
        "\n"
        "- **Check orthogonality**: If the new data reveals that two dimensions are really values on the same axis, merge them. If a dimension conflates two axes, split it.\n"
        "\n"
        "- If an **\"Other\"** or catch-all dimension exists, try to minimize it by re-assigning documents to specific dimensions or creating new specific ones.\n"
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
        "## Q1. Review the dimension-oriented taxonomy against the review criteria. Make adjustments only where a clear quality issue is identified.\n"
        "\n"
        "Tips\n"
        "\n"
        "- **User Feedback is MANDATORY**: You MUST address any previous user feedback.\n"
        "\n"
        "- **Minimal intervention**: Only change what is clearly broken or ambiguous. If the taxonomy is well-structured, return it as-is.\n"
        "\n"
        "- **Do not overfit**: The review sample is small. Do not create dimensions just for edge cases in the sample.\n"
        "\n"
        "- **Check orthogonality**: Ensure each dimension captures a fundamentally different type of distinction. If two dimensions are values on the same axis, merge them. If a dimension conflates two axes, split it.\n"
        "\n"
        "- You may **merge** dimensions that are values on the same axis, **split** dimensions that conflate different axes, **rename** for clarity, or **refine descriptions** for labeling accuracy.\n"
        "\n"
        "- **Max {max_num_clusters} dimensions** total.\n"
        "\n"
        "- If an **\"Other\"** or catch-all dimension exists, try to eliminate it by re-assigning its documents to more specific dimensions.\n"
        "\n"
        "## Q2. What changes did you make (if any) and why? Explain your reasoning **within {explanation_length} words**. If you made no changes, explain why the taxonomy is already adequate as a set of orthogonal dimensions."
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