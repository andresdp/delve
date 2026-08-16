---
type: prompt architecture
title: Prompt templates and structured LLM contracts
description: Markdown-backed prompt loading and the nine prompt-to-model-to-schema contracts used across summarization, coding, taxonomy refinement, consolidation, selection, and labeling.
tags: [prompts, llm, schemas]
---

# Prompt templates and structured LLM contracts

`src/taxonomy_generator/prompts/__init__.py` loads Markdown prompt files at package import time. Missing package data fails import, so prompt text and `pyproject.toml` package-data behavior are part of the runtime contract.

| Template/file | Model | Structured schema | Role |
|---|---|---|---|
| `SUMMARY_GENERATION_PROMPT` / `summary_generation.md` | `fast_llm` | `SummaryOutput` | summarize one document |
| `OPEN_CODING_PROMPT` / `open_coding.md` | `fast_llm` | `OpenCodesOutput` | extract document concepts before grouping |
| `TAXONOMY_GENERATION_PROMPT` / `taxonomy_generation.md` | `model` | `TaxonomyOutput` | create dimensions, values, and relations |
| `TAXONOMY_UPDATE_PROMPT` / `taxonomy_update.md` | `model` | `TaxonomyOutput` | refine the existing design with a new batch |
| `SATURATION_CHECK_PROMPT` / `saturation_check.md` | `fast_llm` | `SaturationCheckOutput` | identify uncovered concepts and saturation |
| `TAXONOMY_REVIEW_PROMPT` / `taxonomy_review.md` | `model` | `TaxonomyOutput` | review a sampled final taxonomy |
| `VALUE_MERGE_PROMPT` / `value_merge.md` | `model` | `ValueMergeOutput` | adjudicate borderline same-decision pairs |
| `DIMENSION_SELECTION_PROMPT` / `dimension_selection.md` | `model` | `SelectionOutput` | retain dimensions relevant to the use case |
| `LABELER_PROMPT` / `labeler.md` | `fast_llm` | `LabelOutput` | classify each document and choose a value when applicable |

Taxonomy chains receive formatted open codes or documents, existing taxonomy JSON where applicable, use-case and length controls, feedback, and a rendered cluster limit. `format_taxonomy` includes relations and values when present. Open coding prefers summaries when available; code-less documents remain visible through a summary fallback.

## Safe change recipe

Preserve prompt variable names or update the partial bindings in the owning node/helper. If changing a response shape, update `schemas.py`, the node mapping, state fields, `utils` formatting, and [CLI/output contracts](../interfaces/cli-and-outputs.md). Validate with `python -c "import taxonomy_generator.prompts"` and graph compilation without network; provider-backed generation, selection, merge adjudication, or labeling is conditional integration validation.