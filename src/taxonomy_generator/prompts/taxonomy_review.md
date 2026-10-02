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
- **A dimension names one axis — never a tradeoff or a set of alternatives.** "X vs. Y Tradeoff" or "Alternative Approaches to X" is not itself an axis of variation: it is usually two dimensions whose interaction belongs in a **relation**, not one dimension named after the fact that a tradeoff exists. Every dimension has alternatives — that's what its values are — so "has alternatives" never distinguishes one dimension from another.

- **A dimension is a decision point: a topic phrased as one question that requires a choice.** Its values are the candidate decisions, i.e. the alternative answers to that question (e.g. dimension "Drift Detection Test", question *which test detects degradation?*, values "CUSUM", "Covariance-weighted mean test"). Check every dimension: can all its values be read as alternative answers to one question? If they answer different questions, the topic is too broad (a theme such as "Governance" or "Robustness Mechanisms") and misleading: split it into the decision points it contains when each keeps at least two candidate decisions, otherwise move its values to the decision points whose questions they answer. Prefer decision points with several candidate decisions over many narrow ones with a single candidate. Values with status `outcome` are effects of decisions, not candidate decisions: a decision point needs at least two candidate decisions (`accepted` or `rejected`). A topic whose values are only outcomes is not a decision point; attach its outcomes to the decision point they result from.

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
| **One decision point** | Can all of a dimension's candidate decisions be read as alternative answers to one question? If they answer different questions, the dimension is a broad topic bundling several decision points, which is misleading. A decision point needs at least two candidate decisions. |
| **Axis vs. value check** | Is each dimension truly an *axis of variation* rather than a single *value*? A dimension named "Bug Reports" might really be a value on an "Issue Type" axis that also includes "Feature Requests", "Questions", etc. |
| **Tradeoff/alternative-shaped naming** | Is any dimension named around "Tradeoff(s)", "Alternative(s)", "Comparison", "Options", or "Choices" rather than the axis itself? These name the existence of a decision, not what distinguishes this axis — a genuine tradeoff usually means two dimensions belong here, linked by a `relations` entry, not one dimension named after the tradeoff. |
| **Quality-attribute grounding** (secondary preference) | Where the use case names quality attributes, forces or concerns, is each decision point's choice driven by recognizable quality attributes, constraints or trade-offs, rather than being an arbitrary topical grouping? This refines *One decision point*; never split, merge or drop a well-formed decision point only because no quality attribute is named. |
| **Rejected-alternative handling** | Is each candidate decision listed once with its stance (`accepted`, `rejected`, or `mixed` when sources disagree), rather than duplicated per status, and is a rejected alternative never presented as adopted? Outcomes (status `outcome`, effects of decisions) are valid values but are kept apart from the candidate decisions. |
| **Candidate-decision coverage** | Do the options that the sampled documents adopt or reject appear as values of the right dimension? Add a missing option as a value of the dimension whose question it answers. |
| **Value-label phrasing** | Is each value's `label` a noun phrase naming the decision or position, rather than a verb-driven sentence? Does any label redundantly restate its `status` as a text prefix (e.g., "Rejected: ...", "Accepted: ...")? |

## Allowed Adjustments

This is a **quality polish**, not a redesign. Only make changes when you identify a clear issue:

| Operation | When to use |
|---|---|
| **Merge dimensions** | Two or more dimensions are really different values on the same underlying axis — they should be one dimension whose description captures the full range. Merge only when both dimensions ask *the same* question. When they ask different questions but share values, move each shared value to the dimension whose question it answers instead: merging two different questions creates a broad topic. |
| **Split dimension** | A dimension conflates two truly orthogonal axes of variation — documents along it actually differ along two fundamentally different types of distinction. |
| **Rename** | A dimension name describes a specific value rather than the axis of variation, is ambiguous, or is built around "Tradeoff(s)"/"Alternative(s)"/"Comparison"/"Options"/"Choices" instead of naming the axis itself. If the tradeoff is genuine, split into the two dimensions and relate them instead of renaming alone. |
| **Refine description** | A description doesn't explain the range of values along the dimension or doesn't differentiate it from other dimensions. |
| **Split broad topic** | A dimension's values answer different questions. Split it into the decision points it contains only when each part keeps at least two candidate decisions; otherwise move each value to the decision point whose question it answers, then remove it. This is a clear issue, so it is allowed despite the minimal-intervention principle. |
| **Merge single-candidate dimensions** | A dimension has only one candidate decision. Merge it into the decision point whose question its value answers, or merge sibling dimensions that answer the same question. Never invent alternatives to fill it. This is a clear issue, so it is allowed despite the minimal-intervention principle. |
| **Remove** | A dimension has no support in the data and is unlikely to be needed (use sparingly). |
| **Add** | Documents in the sample reveal a fundamentally new axis of variation not captured by existing dimensions. Total must still not exceed **{max_num_clusters}**. |
| **No change** | Valid outcome. If the taxonomy is well-structured as a set of orthogonal dimensions, return it as-is. Do not force modifications. |
| **Reclassify value status** | The review sample provides direct evidence that a value's `status` is wrong (e.g., a value marked `accepted` is explicitly declined in the sampled documents). Change `status` only with direct evidence from the sample — never as a side effect of re-emitting the taxonomy. |
| **Relabel value** | A value's `label` restates its `status` as a text prefix, or is phrased as a verb-driven sentence rather than a noun phrase. Rewrite the `label` only — do not change `status`, `description`, or `supporting_doc_ids`. |

## Key Principle: Minimal Intervention

- Only change what is clearly broken or ambiguous.
- **Issues named by the automated evaluation in the previous feedback count as clearly broken.** They concern the taxonomy itself: apply the concrete changes they name (split, merge, move values, rename, add, drop) when they are consistent with the data, even when they restructure a dimension, and move supported values rather than deleting them. Never add a dimension or value that no document supports, even when feedback asks for it.
- Do not overfit to the review sample — it is a small subset, not the full dataset.
- Do not radically restructure — this is a final polish, not a new iteration.

## Requirements

### User Feedback Integration (CRITICAL)
- You MUST incorporate any previous user feedback into your review decisions.
- If specific changes were requested, implement them exactly as specified.

### Format
- Each cluster has: **id** (number starting from 1, incremented), **name** (within {cluster_name_length} words, a noun-driven phrase that describes the *axis of variation* — use noun-based constructions like "Request Routing Strategy" rather than verb-based ones like "Route Requests"), **description** (within {cluster_description_length} words, explaining the range of documents along this dimension and what distinguishes it from other dimensions).
- Total dimensions: **{max_num_clusters}**.
- Each value's **status** (`accepted`, `rejected`, `mixed`, or `outcome`) must be preserved verbatim from the existing taxonomy unless a review adjustment genuinely reclassifies it — never let the field silently default to `accepted` on re-emission.
- Each value's **label** must be preserved verbatim unless a review adjustment relabels it per the **Relabel value** operation below.
- Output in **English** only.

### Quality
- Dimensions must be orthogonal — no two dimensions should capture the same type of distinction.
- Names should describe the axis of variation, not a specific value on that axis.
- Descriptions should explain the range of values along each dimension and differentiate it from other dimensions.
- Dimensions should serve the given use case well.
- Every dimension must be specific enough that a document clearly belongs or doesn't belong.
- **No tradeoff- or alternative-shaped dimensions**: reject dimension names built around "Tradeoff(s)", "Alternative(s)", "Comparison", "Options", or "Choices". If a genuine tradeoff is present, split it into the two dimensions being traded off and connect them with a `relations` entry instead.
- **A value is one position, not a tradeoff between two dimensions**: if a value's label conjoins two distinct concerns (e.g., "X over Y", "X vs Y", "X at the cost of Y"), check whether X and Y are actually two different axes.
- **Value labels are noun phrases, not sentences**: a value's label names the decision or position (e.g., "S3-backed write-ahead log"), not a sentence describing what happened. Never prefix a label with its status (e.g., no "Rejected: ..." or "Accepted: ...") — status is already carried in the **status** field.
