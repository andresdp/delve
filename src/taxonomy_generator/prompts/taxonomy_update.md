# Instruction

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
- Be specific and meaningful. Do not invent categories not in the data.