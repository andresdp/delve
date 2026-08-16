# Instruction

## Context

- **Goal**: Your goal is to identify the **dimensions of variation** in the input data — orthogonal axes along which documents differ — and organize them into a taxonomy for the given use case. Each dimension groups documents that share a fundamentally similar kind of content or purpose.

- **Data**: The input data is a list of documents in JSON format. Each item has:
  - **id**: document index.
  - **codes**: the open codes extracted from that document — fine-grained concept/decision labels with rationales. These are the raw material you organize into dimensions and values (axial coding). When a document has no codes, its entry carries a single code holding the document summary instead.

- **Use case**: {use_case}

- **Previous feedback**: {feedback}

## Design Space Framework

Think of the taxonomy as a **design space**. In this framework:

- Each **category is a dimension** — an axis that captures a fundamentally different *kind* of variation among documents. For example, if classifying software emails, dimensions might be "Bug Reporting", "Feature Design", "Release Coordination" — each representing a distinct axis of intent, not just different points on the same axis.
- Each **document is a value** along exactly one dimension. A document belongs to the dimension whose axis of variation best describes its fundamental character.
- Dimensions must be **orthogonal** — each captures a different *type* of distinction. If two categories are really just different values on the same axis (e.g., "Minor Bugs" vs "Critical Bugs" are both values of a "Bug Severity" axis), they should be one dimension, not two.
- A well-structured taxonomy lets you **characterize the full space** of documents by walking its dimensions, each offering a unique lens through which the data varies.
- Each dimension carries **values** — the specific decisions or positions along its axis that the data supports (e.g., a "Caching Strategy" dimension may hold values like "cache everything", "cache reads only", "no caching"). Values are points on the axis; the dimension is the axis itself.
- Dimensions may be linked by typed **relations** (precondition, consequence, co_occurring, constrains) — grounded theory's paradigm model. Only assert a relation when it holds because of the use case's logic, not because two concepts merely co-occur in the same documents.

## Requirements

### User Feedback Integration (CRITICAL)

- You MUST incorporate any previous user feedback into your clustering decisions
- If specific changes were requested, implement them exactly as specified
- If general feedback was given, ensure your clustering reflects those preferences
- If no feedback exists, proceed with standard clustering

### Format

- Each cluster has:
  - **id**: category number starting from 1, incremented.
  - **name**: dimension name within **{cluster_name_length} words**. A noun-driven phrase that describes the *axis of variation*, not a specific value. Use noun-based constructions (e.g., "Request Routing Strategy", "Data Access Pattern") rather than verb-based ones (e.g., "Route Requests", "Access Data").
  - **description**: dimension description within **{cluster_description_length} words**. Should explain what kind of documents (values) fall along this dimension and what fundamentally distinguishes this axis from other dimensions in the taxonomy.
  - **values**: draft values along this dimension that the open codes support. Each value has an **id** (formatted as `<dimension_id>.<n>`, incremented), **dimension_id** (this cluster's id), **label** (concise decision label), **description**, and **supporting_doc_ids** (ids of documents whose open codes support it). Draft only values the data supports — a dimension may legitimately have no values yet.
  - **relations**: typed links from this dimension to other dimensions, each with **target_id** (the other dimension's id), **type** (`precondition`, `consequence`, `co_occurring`, or `constrains`), and **rationale** judged against the use case. Omit when no genuine relation exists.

- Total number of dimensions: **{max_num_clusters}**. Generate as many distinct, well-supported dimensions as the data warrants to maximize coverage. However, if fewer dimensions better represent the data, prefer quality over quantity.
- Output in **English** only.

### Quality

- **User Feedback Alignment**: Dimensions MUST align with any provided user feedback and preferences.
- **Dimensional coverage**: Generate dimensions that capture the full breadth of variation in the data. Each dimension should represent a fundamentally different *kind* of content, purpose, or intent. Avoid grouping distinct types of variation into a single broad dimension.
- **Orthogonality (critical)**: Each dimension must capture a fundamentally different *type* of distinction — not just a different point on the same axis. If two categories are variations of the same underlying concept (e.g., "Bug Reports" vs "Feature Requests" could be values of an "Issue Type" axis), they should be merged into a single dimension whose description captures the full range of values. Conversely, if a category conflates two truly different axes, split it.
- **Specificity**: Every dimension must be specific enough that a document clearly belongs or doesn't belong. Avoid overly broad catch-all dimensions. Do not invent dimensions that are not supported by the data.
- **Use case relevance**: Dimensions must be directly relevant and useful for the stated use case. Exclude dimensions that don't serve the use case, even if present in the data.
- **Name** is a concise and clear label that describes the *axis of variation*, not a specific value on that axis.
- **Description** explains the range of documents (values) along this dimension and makes the boundary between this dimension and others explicit.
- **Name** and **description** can accurately and consistently classify new data points without ambiguity.
- **Name** and **description** are consistent with each other.

# Data

{data_json}
