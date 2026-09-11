# Instruction

## Context

- **Goal**: Your goal is to **incrementally refine** an existing dimension-oriented taxonomy by incorporating a new batch of data. Each category in the taxonomy represents a **dimension of variation** — an orthogonal axis along which documents differ. You may add, split, merge, rename, or remove dimensions as needed — but changes should be deliberate and balanced.

- **Existing taxonomy**:
{taxonomy_json}

- **New data**: A batch of documents in JSON format with their open codes (fine-grained concept/decision labels with rationales and a **status** — `accepted`, `rejected`, or `outcome` — already classified during open coding):
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
- **A dimension names one axis — never a tradeoff or a set of alternatives.** "X vs. Y Tradeoff" or "Alternative Approaches to X" is not itself an axis of variation: it is usually two dimensions whose interaction belongs in a **relation** (e.g. a `constrains` or `consequence` link between them), not one dimension named after the fact that a tradeoff exists. Every dimension has alternatives — that's what its values are — so "has alternatives" never distinguishes one dimension from another; name the dimension after what actually varies.
- **Quality-attribute anchoring**: Before updating dimensions, name the quality attributes, constraints, or concerns the use case implies (e.g., performance, security, cost, compliance, maintainability — illustrative examples only, not an exhaustive list). Then check the new data and existing dimensions against that list, even when a fit isn't the most textually obvious grouping.

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
- Each cluster also carries: **values** (draft decisions along the dimension supported by the open codes; each value has an **id** formatted as `<dimension_id>.<n>`, **dimension_id**, **label** (a noun phrase, e.g. "S3-backed write-ahead log", not a sentence like "Log writes to S3 before commit"; never prefixed with the status), **description**, **status** (`accepted`, `rejected`, or `outcome`, carried from its supporting codes), and **supporting_doc_ids**) and **relations** (typed links with **target_id**, **type** — `precondition`, `consequence`, `co_occurring`, or `constrains` — and a **rationale** judged against the use case).
- **Preserve existing values** that remain supported; **merge** value drafts from new open codes into existing values only when they share the same status (union their supporting_doc_ids); **add** new values for decisions not yet on the axis, including when a new code's status differs from an existing near-duplicate value's status — never group codes of different status into one value. Never drop values without justification.
- Total dimensions: **{max_num_clusters}**.
- Output in **English** only.

### Quality
- Dimensions must be orthogonal — no two dimensions should capture the same type of distinction.
- Names should describe the axis of variation, not a specific value on that axis.
- Descriptions should explain the range of values along each dimension and differentiate it from other dimensions.
- Dimensions should serve the given use case well.
- Every dimension must be specific enough that a document clearly belongs or doesn't belong.
- **No tradeoff- or alternative-shaped dimensions**: reject dimension names built around "Tradeoff(s)", "Alternative(s)", "Comparison", "Options", or "Choices" — these name the *existence* of a decision, not what makes this axis distinct from every other. If a genuine tradeoff is present, split it into the two dimensions being traded off and connect them with a `relations` entry instead.
- **A value is one position, not a tradeoff between two dimensions**: if a value's label conjoins two distinct concerns (e.g., "X over Y", "X vs Y", "X at the cost of Y"), check whether X and Y are actually two different axes — the value likely belongs on one of two dimensions, not both at once.
- **Value labels are noun phrases, not sentences**: a value's label names the decision or position (e.g., "S3-backed write-ahead log"), not a sentence describing what happened (e.g., "Log writes to S3 before commit"). Never prefix a label with its status (e.g., no "Rejected: ..." or "Accepted: ...") — status is already carried in the **status** field.
