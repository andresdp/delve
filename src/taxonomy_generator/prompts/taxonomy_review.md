# Instruction

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
- Ensure the taxonomy serves the given use case well.