# Instruction

## Context

- **Goal**: Your goal is to **incrementally refine** an existing taxonomy by incorporating a new batch of data. You may add, split, merge, rename, or remove categories as needed — but changes should be deliberate and balanced.

- **Existing taxonomy**:
{taxonomy_json}

- **New data**: A batch of document summaries in JSON format:
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Key Principle: Stability + Adaptability

This is **one batch in a series**. The existing taxonomy was built from previous batches and represents patterns found in earlier data. Your job is to evolve it — not replace it.

- **Preserve** categories that remain relevant and well-supported.
- **Adapt** only when the new data clearly shows gaps, overlaps, or new themes.
- **Balance** the taxonomy must represent ALL data seen so far, not just this batch. Do not overfit to the new data.

## Handling "Other" or Catch-all Categories

If the existing taxonomy contains a vague or catch-all category (e.g., "Other", "Miscellaneous", "General", "Unclear"):
- **Prioritize absorbing it**: Check whether documents that would fall into "Other" can instead fit into existing specific categories by slightly broadening their scope or descriptions.
- **Create specific alternatives**: If multiple documents in the new batch would be "Other" and share a common theme, create a new specific category for them instead.
- **Goal**: Minimize the need for a catch-all category over successive iterations. The ideal taxonomy has no "Other" — every document should fit a meaningful category.

## Allowed Operations

Apply these **only when clearly justified** by the new data:

| Operation | When to use |
|---|---|
| **Add** | A distinct new theme emerges that no existing category covers. The total must still not exceed **{max_num_clusters}** — merge or remove before adding if at the limit. |
| **Split** | An existing category is too broad — the new data reveals two or more distinct sub-topics. |
| **Merge** | Two or more categories overlap significantly, and the new data confirms they should be one. |
| **Rename / Refine** | A category name or description is unclear or doesn't accurately reflect its scope. |
| **Remove** | A category has no support in any data seen so far (use sparingly). |

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your update decisions.
- If specific changes were requested, implement them exactly as specified.

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, verb or noun phrase), **description** (within {cluster_description_length} words).
- Total categories: **no more than {max_num_clusters}**.
- Output in **English** only.

### Quality
- No overlap or contradiction among categories.
- Names should be concise and specific to each category.
- Descriptions should differentiate one category from another.
- Categories should serve the given use case well.
- Every category must be specific enough that a document clearly belongs or doesn't belong.