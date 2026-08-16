---
type: wiki entrypoint
title: Delve code wiki quickstart
description: Entry guide to the Delve taxonomy-generation repository, its runtime pipeline, public interfaces, configuration, outputs, and validation routes.
tags: [quickstart, navigation, delve]
---

# Delve code wiki quickstart

Delve is a Python package and CLI that accepts a text or JSON corpus, optionally summarizes it, builds an LLM-generated taxonomy through minibatch refinement and review, then labels every document. The compiled LangGraph is the runtime center; `main.py` is the human-facing CLI and serializer.

## Start here

- [Architecture overview](architecture/overview.md) — package boundaries, entrypoints, dependencies, and system flow.
- [Graph and orchestration](pipeline/graph.md) — node topology, conditional routing, reducers, and lifecycle invariants.
- [Ingestion and preprocessing](pipeline/ingestion-and-preprocessing.md) — file formats, normalization, sampling, summaries, and batches.
- [Taxonomy lifecycle](pipeline/taxonomy.md) — generation, updates, review, prompt roles, and iteration semantics.
- [Document classification](pipeline/classification.md) — final taxonomy use, concurrency, labels, scores, and fallback behavior.
- [State and schemas](data-model/state-and-schemas.md) — `Doc`, graph state, reducers, feedback, and Pydantic output contracts.
- [Configuration and settings](configuration/settings.md) — YAML, defaults, overrides, cache lifecycle, provider configuration, and known documentation discrepancies.
- [Public Python API](interfaces/public-api.md) — `taxonomy_generator` exports, `graph.ainvoke`, packaging, and extension boundaries.
- [CLI and output contracts](interfaces/cli-and-outputs.md) — flags, streaming behavior, graph export, and JSON files.
- [Prompt system](prompts/prompt-system.md) — five Markdown-backed templates and their model/schema coupling.
- [Examples and validation](examples-and-validation.md) — corpus inventory, generated artifacts, stale test targets, and non-network checks.

## Runtime map

```mermaid
flowchart LR
    Corpus["corpus file or documents"] --> Ingest["load and normalize"]
    Ingest --> Optional["summarize or skip"]
    Optional --> Batch["shuffle and batch indices"]
    Batch --> Gen["generate taxonomy"]
    Gen --> Refine["update per minibatch"]
    Refine --> Review["review final sample"]
    Review --> Label["label documents"]
    Label --> Result["graph result and CLI JSON"]
```

This is the shortest conceptual route through the runtime; exact edges and reducers are in [Graph and orchestration](pipeline/graph.md).

## Task routing

| Intent/change area | Canonical page | Source entrypoints/symbols | Focused checks / minimal validation |
|---|---|---|---|
| Understand or change graph ordering/routing | [Graph](pipeline/graph.md) | `graph.py:builder`, `graph`, `should_summarize`, `should_review` | Import/compile graph; inspect empty-input and batch invariants |
| Change corpus files, sampling, summaries, or batches | [Ingestion](pipeline/ingestion-and-preprocessing.md) | `main.load_corpus`, `strings_to_docs`, `docs_from_dicts`, `load_corpus`, `generate_summaries`, `_create_batches` | Safe TXT/JSON conversion; `_create_batches`; no-network imports |
| Change taxonomy semantics or refinement | [Taxonomy](pipeline/taxonomy.md) and [Prompts](prompts/prompt-system.md) | `generate_taxonomy`, `update_taxonomy`, `review_taxonomy`, `invoke_taxonomy_chain` | Prompt import and graph compile; provider smoke only when intentional |
| Change labels, scores, fallback, or classification concurrency | [Classification](pipeline/classification.md) | `label_documents`, `_label_single_doc`, `LabelOutput` | Schema/helper imports; missing-cluster failure; provider smoke conditional |
| Change a record, reducer, or LLM response field | [State and schemas](data-model/state-and-schemas.md) | `Doc`, `State`, `UserFeedback`, `SummaryOutput`, `TaxonomyOutput`, `LabelOutput` | Import schemas; update prompt/node/serializer together |
| Add or change a setting | [Configuration](configuration/settings.md) | `Settings`, `_build_*`, `Configuration`, `_defaults_from_settings`, `init_settings` | Load checked-in and temporary YAML; verify override mapping |
| Change Python imports or installation behavior | [Public API](interfaces/public-api.md) | `__all__`, `pyproject.toml`, `langgraph.json`, `main:main` | Import/export list; graph import; package build if available |
| Change CLI flags, Rich display, graph PNG, or JSON files | [CLI/output](interfaces/cli-and-outputs.md) | `parse_args`, `run`, `TokenTracker`, display helpers | `python main.py --help`; non-network serializer/parser checks |
| Add or modify an example | [Examples/validation](examples-and-validation.md) | `examples/prepare_decisions_corpus.py`, `EXAMPLES.md` | Confirm source input exists; distinguish generated output from tests |
| Investigate tests, lint, or documentation automation | [Examples/validation](examples-and-validation.md) | `Makefile`, `.github/workflows/openwiki-update.yml` | Test targets are stale/missing locally; inspect workflow separately |

## Operational notes

A real pipeline run requires a configured LangChain provider and network/API access unless using a locally available provider. The repository's current YAML is `config.yaml`; CLI model flags and `RunnableConfig.configurable` values override it. The README's claims that `LLM_MODEL` and `LLM_FAST_MODEL` override YAML are not implemented by the current settings loader. Do not treat timestamped `output/` or `examples/` artifacts as tests or source truth.

No automated test files were found even though the `Makefile` advertises pytest targets. Begin with the non-network commands in [Examples and validation](examples-and-validation.md), then use a provider-backed smoke run only as conditional integration validation.
