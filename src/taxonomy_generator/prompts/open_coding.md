# Instruction

## Context

- **Goal**: Perform **open coding** — extract fine-grained concept and decision labels from a single document, before any grouping or clustering. These open codes are the raw material that a later axial-coding step organizes into taxonomy dimensions and values.

- **Use case**: {use_case}

- The use case scopes what counts as relevant: extract concepts and decisions that matter *to the stated design space*, not generic entities.

## What is an Open Code

An open code is a short, descriptive label for one concept, decision, property, or action found in the document — grounded in the document's own content, in the analyst's words (not necessarily the document's words).

Good open codes:

- Name a **concept or decision** (e.g., "caching layer chosen", "latency budget exceeded", "team disagrees on framework"), not a generic entity ("database") or a whole-document summary.
- Are **fine-grained**: one code per distinct concept; a rich document yields several codes, a sparse one may yield few or none.
- Carry a **rationale** explaining why the code applies, judged against the use case.

## Requirements

- Extract between 0 and 8 codes per document. Only extract what the document actually supports.
- Every code must be relevant to the use case; ignore incidental content.
- Output codes in **English** only.
- The `doc_id` of every code must exactly match the document id given below.

# Document

- **Id**: {doc_id}

{content}