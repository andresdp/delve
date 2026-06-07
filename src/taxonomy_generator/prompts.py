"""Default prompts used by the agent."""

from langchain_core.prompts import ChatPromptTemplate

SUMMARY_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Your task is to generate a concise summary and explanation of a piece of text.

## Guidelines

- **Summary**: Capture the main topic, intent, or purpose of the text in {summary_length} words or fewer.
- **Explanation**: Provide a brief explanation of the key points or themes in {explanation_length} words or fewer.

You must respond with a JSON object containing:
- "summary": your summary
- "explanation": your explanation"""),
    ("human", """Summarize the following text:

{content}""")
])

TAXONOMY_UPDATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """# Instruction

## Context

- **Goal**: Your goal is to update an existing taxonomy by incorporating new data. You may add, merge, rename, or remove categories as needed.

- **Existing taxonomy**:
{taxonomy_json}

- **Data**: The input data is a list of conversation summaries in JSON format:
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your clustering decisions
- If specific changes were requested, implement them exactly as specified

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, verb or noun phrase), **description** (within {cluster_description_length} words).
- Total categories: **no more than {max_num_clusters}**.
- Output in **English** only.

### Quality
- No overlap or contradiction among categories.
- Names should be concise and specific to each category.
- Descriptions should differentiate one category from another.
- Categories should serve the given use case well.
- Be specific and meaningful. Do not invent categories not in the data."""),
    ("human", "Update the taxonomy based on the new data provided above.")
])

TAXONOMY_REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """# Instruction

## Context

- **Goal**: Your goal is to review and refine an existing taxonomy. Evaluate whether the categories are well-defined, non-overlapping, and cover the data well. Make adjustments as needed.

- **Existing taxonomy**:
{taxonomy_json}

- **Data**: A sample of conversation summaries for reference:
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your review decisions

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, verb or noun phrase), **description** (within {cluster_description_length} words).
- Total categories: **no more than {max_num_clusters}**.
- Output in **English** only.

### Quality
- No overlap or contradiction among categories.
- Names should be concise and specific.
- Descriptions should differentiate categories clearly.
- Categories should be orthogonal and cover the target domain.
- Remove vague categories like "Other", "General", "Miscellaneous".
- Ensure the taxonomy serves the given use case well."""),
    ("human", "Review the taxonomy and make any necessary improvements.")
])

LABELER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Your task is to use the provided taxonomy to categorize the overall topic or intent of a conversation between a human and an AI assistant.

First, here is the taxonomy to use:

{taxonomy_json}

To complete the task:

1. Carefully read through the entire conversation, paying attention to the key topics discussed and the apparent intents behind the human's messages.

2. Consult the taxonomy and identify the single most relevant category that best captures the overall topic or intent of the conversation.

3. Write out a chain of reasoning for why you selected that category. Explain how the category fits the content of the conversation, referencing specific statements or passages as evidence.

4. If by any chance no category fits the content nicely, use the category '{fallback_category}'.

You must respond with a JSON object containing:
- "reasoning": your chain of reasoning
- "category": the name of the category you chose (just the text, no number)

Remember, choose the single most relevant category. Don't choose multiple categories. Think it through carefully and explain your reasoning before giving your final category choice."""),
    ("human", """Assign a single category to the following content:

{content}""")
])

TAXONOMY_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """# Instruction

## Context

- **Goal**: Your goal is to cluster the input data into meaningful categories for the given use case.

- **Data**: The input data is a list of conversation summaries in JSON format. Each item has:
  - **id**: conversation index.
  - **summary**: conversation summary text.

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Requirements

### User Feedback Integration (CRITICAL)

- You MUST incorporate any previous user feedback into your clustering decisions
- If specific changes were requested, implement them exactly as specified
- If general feedback was given, ensure your clustering reflects those preferences
- If no feedback exists, proceed with standard clustering

### Format

- Each cluster has:
  - **id**: category number starting from 1, incremented.
  - **name**: category name within **{cluster_name_length} words**. Verb phrase or noun phrase.
  - **description**: category description within **{cluster_description_length} words**.

- Total number of categories: **no more than {max_num_clusters}**.
- Output in **English** only.

### Quality

- **User Feedback Alignment**: Clusters MUST align with any provided user feedback and preferences.
- **No overlap or contradiction** among the categories.
- **Name** is a concise and clear label, specific to each category.
- **Description** differentiates one category from another.
- **Name** and **description** can accurately and consistently classify new data points without ambiguity.
- **Name** and **description** are consistent with each other.
- Output clusters match the data as closely as possible, without missing important categories or adding unnecessary ones.
- Output clusters should be orthogonal, providing solid coverage of the target domain.
- Output clusters serve the given use case well.
- Be specific and meaningful. Do not invent categories that are not in the data.

# Data

{data_json}"""),
    ("human", """# Questions

## Q1. Please generate a cluster table from the input data that meets the requirements.

Tips

- **User Feedback is MANDATORY**: You MUST address any previous user feedback in your clustering
- If user feedback was provided, explicitly explain how you've incorporated their specific concerns and suggestions

- The cluster table should be a **flat list** of **mutually exclusive** categories. Sort them based on their semantic relatedness.

- Though you should aim for {max_num_clusters} categories, you can have *fewer than {max_num_clusters} categories*; but **do not exceed the limit.**

- Be **specific** about each category. **Do not include vague categories** such as "Other", "General", "Unclear", "Miscellaneous" or "Undefined" in the cluster table.

- You can ignore low quality or ambiguous data points.

## Q2. Why did you cluster the data the way you did? Explain your reasoning **within {explanation_length} words**. Include how you addressed any user feedback.""")
])