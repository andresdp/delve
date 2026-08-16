---
type: prompt architecture
title: Prompt templates and structured LLM contracts
description: Markdown-backed prompt loading and the five prompt-to-model-to-schema contracts used by Delve.
tags: [prompts, llm, schemas]
---

# Prompt templates and structured LLM contracts

`prompts/__init__.py` loads five Markdown system files with `_load_prompt` and pairs each with an inline human message in a `ChatPromptTemplate`. Loading occurs at package import time, so missing package files fail import and prompt edits are runtime behavior changes.

| Template and file | Human input | Bound model | Structured schema | Key variables |
|---|---|---|---|---|
| `SUMMARY_GENERATION_PROMPT` / `summary_generation.md` | `{content}` | `Configuration.fast_llm` | `SummaryOutput` | `use_case`, `summary_length`, `explanation_length` |
| `TAXONOMY_GENERATION_PROMPT` / `taxonomy_generation.md` | data/questions | `Configuration.model` | `TaxonomyOutput` | feedback, use case, lengths, max dimensions |
| `TAXONOMY_UPDATE_PROMPT` / `taxonomy_update.md` | new batch/questions | `Configuration.model` | `TaxonomyOutput` | same taxonomy controls plus existing taxonomy/data JSON |
| `TAXONOMY_REVIEW_PROMPT` / `taxonomy_review.md` | review questions | `Configuration.model` | `TaxonomyOutput` | same controls and review sample context |
| `LABELER_PROMPT` / `labeler.md` | `{content}` | `Configuration.fast_llm` | `LabelOutput` | `fallback_category`, `use_case`, `taxonomy_json` |

Taxonomy chains receive `data_json`, `taxonomy_json`, `use_case`, `suggestion_length`, `cluster_name_length`, `cluster_description_length`, `explanation_length`, and a rendered `max_num_clusters`. `invoke_taxonomy_chain` supplies these and appends the returned clusters/explanation. Generation/update/review prompts require orthogonal, use-case-relevant dimensions and discourage vague catch-alls. `format_feedback` supplies `None.` when no feedback exists.

## Safe change recipe

When changing a prompt, preserve its variable names or update the partial bindings in the owning node/helper. If changing output shape, update the Pydantic schema, node mapping, `utils` formatting, and [CLI/output contracts](../interfaces/cli-and-outputs.md). Summary and labeling use bounded concurrency; taxonomy stages use the reasoning model. Validate prompt import with `python -c "import taxonomy_generator.prompts"` and compile the graph without network calls; provider-backed behavior requires a configured model/key and is not a deterministic test.
