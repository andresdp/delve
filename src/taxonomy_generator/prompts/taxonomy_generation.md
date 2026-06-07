# Instruction

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

{data_json}