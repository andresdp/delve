# Instruction

## Context

- **Goal**: Your goal is to cluster the input data into meaningful, diverse, and representative categories for the given use case.

- **Data**: The input data is a list of document summaries in JSON format. Each item has:
  - **id**: document index.
  - **summary**: document summary text.

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

- Total number of categories: **no more than {max_num_clusters}**. Generate as many distinct, well-supported categories as the data warrants — up to this limit — to maximize coverage. However, if fewer categories better represent the data, prefer quality over quantity. **Do not exceed the limit.**
- Output in **English** only.

### Quality

- **User Feedback Alignment**: Clusters MUST align with any provided user feedback and preferences.
- **Diversity**: Generate categories that capture the full breadth of themes present in the data. Avoid clustering everything into a few broad groups when distinct patterns exist.
- **Orthogonality**: Each category must capture a distinct, non-overlapping aspect of the data. If two categories could contain the same document, merge or refine them. Categories should be mutually exclusive with no contradiction among them.
- **Specificity**: Every category must be specific enough that a document clearly belongs or doesn't belong. Avoid overly broad catch-all categories. Do not invent categories that are not supported by the data.
- **Use case relevance**: Categories must be directly relevant and useful for the stated use case. Exclude categories that don't serve the use case, even if present in the data.
- **Name** is a concise and clear label, specific to each category.
- **Description** differentiates one category from another and makes the boundaries between categories explicit.
- **Name** and **description** can accurately and consistently classify new data points without ambiguity.
- **Name** and **description** are consistent with each other.

# Data

{data_json}