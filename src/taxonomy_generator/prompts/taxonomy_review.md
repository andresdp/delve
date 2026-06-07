# Instruction

## Context

- **Goal**: Your goal is to perform a **final quality review** of the taxonomy before it is used for document classification. This is the last opportunity to catch issues — after this, the taxonomy will be used as-is to label all documents.

- **Existing taxonomy**:
{taxonomy_json}

- **Review sample**: A random sample of document summaries for validation:
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Review Criteria

Evaluate the taxonomy against these dimensions:

| Criterion | What to check |
|---|---|
| **Coverage** | Can every document in the sample be classified into at least one category? Are there documents that fall outside all categories? |
| **Distinctness** | Are categories clearly differentiated? Could a document reasonably fit into two or more categories? If so, those categories may need merging or sharper definitions. |
| **Clarity** | Are category names and descriptions clear enough that a labeler could classify documents accurately without ambiguity? |
| **Completeness** | Are all major themes from the data captured? Are there recurring patterns that no category represents? |
| **Use case alignment** | Does every category serve the stated use case? Remove categories that are irrelevant, even if they exist in the data. |
| **No catch-alls** | Does the taxonomy contain an "Other", "Miscellaneous", or similar vague category? Can those documents be re-assigned to more specific categories instead? |

## Allowed Adjustments

This is a **quality polish**, not a redesign. Only make changes when you identify a clear issue:

| Operation | When to use |
|---|---|
| **Merge** | Two or more categories overlap significantly — documents could fit into either one. |
| **Split** | A category is too broad or acts as a catch-all, making accurate labeling difficult. |
| **Rename** | A category name is ambiguous, inconsistent, or not descriptive enough for classification. |
| **Refine description** | A description is vague, insufficient for labeling, or doesn't differentiate from other categories. |
| **Remove** | A category has no support in the data and is unlikely to be needed (use sparingly). |
| **Add** | Documents in the sample clearly fall outside all existing categories. Total must still not exceed **{max_num_clusters}**. |
| **No change** | Valid outcome. If the taxonomy is well-structured, return it as-is. Do not force modifications. |

## Key Principle: Minimal Intervention

- Only change what is clearly broken or ambiguous.
- Do not overfit to the review sample — it is a small subset, not the full dataset.
- Do not radically restructure — this is a final polish, not a new iteration.

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your review decisions.
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