---
type: pipeline domain
title: Document classification
description: Final-taxonomy selection, bounded parallel LLM labeling, confidence and value records, fallback behavior, and classification messages.
tags: [classification, pipeline, llm]
---

# Document classification

`nodes/doc_labeler.py:label_documents` runs after dimension selection. It searches `state.clusters` in reverse for the latest non-empty complete taxonomy iteration and formats dimensions, relations, and values for the fast-model `LABELER_PROMPT`. It raises `ValueError` when no valid taxonomy exists. The node does not currently consume `selected_clusters`, so selection is a separately exposed use-case view rather than the classifier's input.

Each document is labeled through `_label_single_doc` under an `asyncio.Semaphore` sized by `summary_max_concurrency`. `asyncio.gather` preserves input ordering. The node reconstructs `Doc` records with original ID/content/summary, model reasoning in `explanation`, category, and score, then emits an `AIMessage` and success status. `LabelOutput.value_id` can identify a specific value, but the current `Doc` reconstruction does not copy that field into `Doc.value`.

The configured `fallback_category` is supplied in the prompt; it is not forcibly inserted into model output or taxonomy state. CLI rendering creates a virtual fallback branch when needed, while serialized generated clusters remain distinct from that display-only branch. See [CLI and output contracts](../interfaces/cli-and-outputs.md).

## Invariants and validation

Classification must preserve document ordering and use a valid final taxonomy. Changes to label fields span `doc_labeler.py`, `schemas.py`, `state.py`, prompt text, message formatting, and JSON serialization. The narrow checks are schema/helper imports and `python main.py --help`; a real label smoke test requires a configured provider.