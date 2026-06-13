# Instruction

## Context

- **Goal**: Your goal is to perform a **final quality review** of the dimension-oriented taxonomy before it is used for document classification. Each category represents a **dimension of variation** — an orthogonal axis along which documents differ. This is the last opportunity to catch issues — after this, the taxonomy will be used as-is to label all documents.

- **Existing taxonomy**:
{taxonomy_json}

- **Review sample**: A random sample of document summaries for validation:
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Design Space Framework

Think of the taxonomy as a **design space**:

- Each **category is a dimension** — an axis that captures a fundamentally different *kind* of variation among documents.
- Each **document is a value** along exactly one dimension.
- Dimensions must be **orthogonal** — each captures a different *type* of distinction.

## Review Criteria

Evaluate the taxonomy against these criteria:

| Criterion | What to check |
|---|---|
| **Dimensional coverage** | Can every document in the sample be placed along at least one dimension? Are there documents that don't fit any dimension's axis of variation? |
| **Orthogonality** | Are dimensions truly orthogonal — does each capture a fundamentally different *type* of distinction? If two dimensions are really just different values on the same underlying axis (e.g., "Bug Reports" and "Feature Requests" are both values of "Issue Type"), they should be merged into one dimension. |
| **Clarity** | Are dimension names and descriptions clear enough that a labeler could classify documents accurately without ambiguity? Does the description explain what kind of values (documents) fall along this axis? |
| **Completeness** | Are all major axes of variation from the data captured? Are there recurring patterns of variation that no dimension represents? |
| **Use case alignment** | Does every dimension serve the stated use case? Remove dimensions that are irrelevant, even if they exist in the data. |
| **No catch-alls** | Does the taxonomy contain an "Other", "Miscellaneous", or similar vague dimension? Can those documents be re-assigned to more specific dimensions instead? |
| **Axis vs. value check** | Is each dimension truly an *axis of variation* rather than a single *value*? A dimension named "Bug Reports" might really be a value on an "Issue Type" axis that also includes "Feature Requests", "Questions", etc. |

## Allowed Adjustments

This is a **quality polish**, not a redesign. Only make changes when you identify a clear issue:

| Operation | When to use |
|---|---|
| **Merge dimensions** | Two or more dimensions are really different values on the same underlying axis — they should be one dimension whose description captures the full range. |
| **Split dimension** | A dimension conflates two truly orthogonal axes of variation — documents along it actually differ along two fundamentally different types of distinction. |
| **Rename** | A dimension name describes a specific value rather than the axis of variation, or is ambiguous. |
| **Refine description** | A description doesn't explain the range of values along the dimension or doesn't differentiate it from other dimensions. |
| **Remove** | A dimension has no support in the data and is unlikely to be needed (use sparingly). |
| **Add** | Documents in the sample reveal a fundamentally new axis of variation not captured by existing dimensions. Total must still not exceed **{max_num_clusters}**. |
| **No change** | Valid outcome. If the taxonomy is well-structured as a set of orthogonal dimensions, return it as-is. Do not force modifications. |

## Key Principle: Minimal Intervention

- Only change what is clearly broken or ambiguous.
- Do not overfit to the review sample — it is a small subset, not the full dataset.
- Do not radically restructure — this is a final polish, not a new iteration.

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your review decisions.
- If specific changes were requested, implement them exactly as specified.

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, a noun-driven phrase that describes the *axis of variation* — use noun-based constructions like "Request Routing Strategy" rather than verb-based ones like "Route Requests"), **description** (within {cluster_description_length} words, explaining the range of documents along this dimension and what distinguishes it from other dimensions).
- Total dimensions: **{max_num_clusters}**.
- Output in **English** only.

### Quality
- Dimensions must be orthogonal — no two dimensions should capture the same type of distinction.
- Names should describe the axis of variation, not a specific value on that axis.
- Descriptions should explain the range of values along each dimension and differentiate it from other dimensions.
- Dimensions should serve the given use case well.
- Every dimension must be specific enough that a document clearly belongs or doesn't belong.
