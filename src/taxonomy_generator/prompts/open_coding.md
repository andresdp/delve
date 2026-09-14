# Instruction

## Context

- **Goal**: Perform **open coding** — extract fine-grained concept and decision labels from a single document, before any grouping or clustering. These open codes are the raw material that a later axial-coding step organizes into taxonomy dimensions and values.

- **Use case**: {use_case}

- The use case scopes what counts as relevant: extract concepts and decisions that matter *to the stated design space*, not generic entities.

## What is an Open Code

An open code is a short, descriptive label for one concept, decision, property, or action found in the document — grounded in the document's own content, in the analyst's words (not necessarily the document's words).

Good open codes:

- Name a **concept or decision** as a **noun phrase** (e.g., "Redis-backed caching layer", "latency budget", "framework disagreement"), never a verb-driven sentence ("caching layer chosen", "latency budget exceeded", "team disagrees on framework"), a generic entity ("database"), or a whole-document summary.
- Are **fine-grained**: one code per distinct concept; a rich document yields several codes, a sparse one may yield few or none.
- Carry a **rationale** explaining why the code applies, judged against the use case.

## Decision Status

Every open code must also carry a `status`, classified from **the document's own framing** — not from what the analyst would choose:

- `accepted` — the source content adopted this decision (e.g., "We chose Redis for the caching layer.").
- `rejected` — the source content explicitly declined this decision (e.g., "We considered GraphQL but decided against it." — even if the document praises GraphQL's merits, this is still `rejected` because the document says it was not adopted).
- `outcome` — the source content merely reports this as a trade-off or result, not a decision being made (e.g., "Latency dropped to 50ms after the change." is an outcome, not a decision).

`status` is the **authoritative** field for downstream filtering and merging — it is what later stages use to decide, for example, whether a code represents an adopted decision. `rationale` still explains *why* the code applies, but its wording must not contradict `status` (e.g., do not write a rationale that reads as endorsing an option while marking it `rejected`). Never restate `status` as a text prefix in the `label` itself (e.g., no "Rejected: GraphQL for the API" — write the label as "GraphQL for the API" and set `status` to `rejected` separately); the label names the concept, the field carries the status.

## Requirements

- Extract between 0 and 8 codes per document. Only extract what the document actually supports.
- Every code must be relevant to the use case; ignore incidental content.
- Output codes in **English** only.
- The `doc_id` of every code must exactly match the document id given below.

# Document

- **Id**: {doc_id}

{content}