---
type: pipeline domain
title: Document classification
description: Final-taxonomy selection, bounded parallel LLM labeling, confidence records, fallback behavior, and classification messages.
tags: [classification, pipeline, llm]
---

# Document classification

`nodes/doc_labeler.py:label_documents` runs after review. It searches `state.clusters` in reverse for the latest non-empty list, formats that taxonomy as `{id,name,description}`, and raises `ValueError` if no valid clusters exist. It builds a fast-model chain using `LABELER_PROMPT` and `LabelOutput`.

Every working document is labeled concurrently through `_label_single_doc` under an `asyncio.Semaphore` sized by `summary_max_concurrency`. The result's `category`, `score`, and `reasoning` are copied into a new `Doc`; original id/content and summary are retained. The node also emits an `AIMessage` containing a readable classification report and a success status.

The configured `fallback_category` is passed into the prompt as the category to use when no taxonomy category fits. It is not forcibly inserted into the model result or taxonomy state. CLI tree/output rendering adds a virtual fallback cluster when documents use that category but the generated taxonomy does not contain it; see [CLI and output contracts](../interfaces/cli-and-outputs.md).

## Invariants and change surface

Classification must consume the final reviewed taxonomy and preserve document ordering through `asyncio.gather`/zip pairing. `score` is intended as 0.0–1.0 confidence but is not range-validated in `LabelOutput`. Changes to label fields span the prompt, schema, `Doc`, message formatting, and JSON serialization. The focused source failure is missing clusters; no automated tests are present. A non-network check can import `_format_results` and schema classes; a real label smoke test requires an LLM provider.
