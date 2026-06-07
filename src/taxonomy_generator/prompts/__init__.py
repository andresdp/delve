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
        "- Though you should aim for {max_num_clusters} categories, you can have *fewer than {max_num_clusters} categories*; but **do not exceed the limit.**\n"
        "\n"
        "- Be **specific** about each category. **Do not include vague categories** such as \"Other\", \"General\", \"Unclear\", \"Miscellaneous\" or \"Undefined\" in the cluster table.\n"
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
    "Update the taxonomy based on the new data provided above.",
)

# ---------------------------------------------------------------------------
# Taxonomy review
# ---------------------------------------------------------------------------

TAXONOMY_REVIEW_PROMPT = _load_prompt(
    "taxonomy_review.md",
    "Review the taxonomy and make any necessary improvements.",
)

# ---------------------------------------------------------------------------
# Document labeling
# ---------------------------------------------------------------------------

LABELER_PROMPT = _load_prompt(
    "labeler.md",
    "Assign a single category to the following content:\n\n{content}",
)

__all__ = [
    "SUMMARY_GENERATION_PROMPT",
    "TAXONOMY_GENERATION_PROMPT",
    "TAXONOMY_UPDATE_PROMPT",
    "TAXONOMY_REVIEW_PROMPT",
    "LABELER_PROMPT",
]