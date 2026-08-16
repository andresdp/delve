# Instruction

## Context

- **Goal**: Your goal is to **incrementally refine** an existing dimension-oriented taxonomy by incorporating a new batch of data. Each category in the taxonomy represents a **dimension of variation** — an orthogonal axis along which documents differ. You may add, split, merge, rename, or remove dimensions as needed — but changes should be deliberate and balanced.

- **Existing taxonomy**:
{taxonomy_json}

- **New data**: A batch of documents in JSON format with their open codes (fine-grained concept/decision labels with rationales):
{data_json}

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Design Space Framework

Think of the taxonomy as a **design space**:

- Each **category is a dimension** — an axis that captures a fundamentally different *kind* of variation among documents.
- Each **document is a value** along exactly one dimension.
- Dimensions must be **orthogonal** — each captures a different *type* of distinction. If two categories are really just different values on the same axis (e.g., "Minor Bugs" vs "Critical Bugs" are both values of a "Bug Severity" axis), they should be one dimension, not two.
- Each dimension carries **values** — the specific decisions or positions along its axis supported by the data. Values are points on the axis; the dimension is the axis itself.
- Dimensions may be linked by typed **relations** (precondition, consequence, co_occurring, constrains). Only assert a relation when it holds because of the use case's logic, not because two concepts merely co-occur in the same documents.

## Key Principle: Stability + Adaptability

This is **one batch in a series**. The existing taxonomy was built from previous batches and represents patterns found in earlier data. Your job is to evolve it — not replace it.

- **Preserve** dimensions that remain relevant and well-supported.
- **Adapt** only when the new data clearly shows gaps, overlaps, or new axes of variation.
- **Balance** the taxonomy must represent ALL data seen so far, not just this batch. Do not overfit to the new data.

## Handling "Other" or Catch-all Dimensions

If the existing taxonomy contains a vague or catch-all dimension (e.g., "Other", "Miscellaneous", "General", "Unclear"):
- **Prioritize absorbing it**: Check whether documents that would fall into "Other" can instead fit into existing specific dimensions by slightly broadening their scope or descriptions.
- **Create specific alternatives**: If multiple documents in the new batch would be "Other" and share a common axis of variation, create a new specific dimension for them instead.
- **Goal**: Minimize the need for a catch-all dimension over successive iterations. The ideal taxonomy has no "Other" — every document should fit along a meaningful dimension.

## Dimension-Oriented Operations

Apply these **only when clearly justified** by the new data:

| Operation | When to use |
|---|---|
| **Add dimension** | A fundamentally new axis of variation emerges that no existing dimension captures. The total must still not exceed **{max_num_clusters}**. |
| **Split dimension** | An existing dimension conflates two truly different axes of variation — the new data reveals that documents along this dimension actually differ along two orthogonal axes. |
| **Merge dimensions** | Two or more dimensions are really just different values on the same underlying axis (e.g., "Bug Reports" and "Feature Requests" are both values of an "Issue Type" axis). Merge them into one dimension whose description captures the full range. |
| **Rename / Refine** | A dimension name or description is unclear, doesn't accurately describe the axis of variation, or conflates values that belong to different axes. |
| **Remove** | A dimension has no support in any data seen so far (use sparingly). |

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your update decisions.
- If specific changes were requested, implement them exactly as specified.

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, a noun-driven phrase that describes the *axis of variation* — use noun-based constructions like "Request Routing Strategy" rather than verb-based ones like "Route Requests"), **description** (within {cluster_description_length} words, explaining the range of documents along this dimension and what distinguishes it from other dimensions).
- Each cluster also carries: **values** (draft decisions along the dimension supported by the open codes; each value has an **id** formatted as `<dimension_id>.<n>`, **dimension_id**, **label**, **description**, and **supporting_doc_ids**) and **relations** (typed links with **target_id**, **type** — `precondition`, `consequence`, `co_occurring`, or `constrains` — and a **rationale** judged against the use case).
- **Preserve existing values** that remain supported; **merge** value drafts from new open codes into existing values (union their supporting_doc_ids); **add** new values only for decisions not yet on the axis. Never drop values without justification.
- Total dimensions: **{max_num_clusters}**.
- Output in **English** only.

### Quality
- Dimensions must be orthogonal — no two dimensions should capture the same type of distinction.
- Names should describe the axis of variation, not a specific value on that axis.
- Descriptions should explain the range of values along each dimension and differentiate it from other dimensions.
- Dimensions should serve the given use case well.
- Every dimension must be specific enough that a document clearly belongs or doesn't belong.
