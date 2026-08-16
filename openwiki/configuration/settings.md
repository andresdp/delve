---
type: configuration reference
title: Configuration and settings resolution
description: YAML-backed settings, runtime overrides, model and embedding providers, consolidation and visualization controls, and effective-value caveats.
tags: [configuration, settings, operations]
---

# Configuration and settings resolution

`settings.py` defines frozen nested dataclasses composed into `Settings`; `load_settings(config_path)` reads the supplied YAML or `config.yaml` in the current working directory. `Configuration` maps resolved settings to LangGraph fields and caches them until `init_settings` reloads the cache. Unknown YAML keys and value ranges are not centrally validated.

## Effective precedence

| Priority | Source | Scope |
|---|---|---|
| 1 | `RunnableConfig.configurable` | matching flat `Configuration` fields |
| 2 | YAML | settings mapped by `Configuration._defaults_from_settings` |
| 3 | Python defaults | missing file/keys |

`main.run` overrides model, fast model, taxonomy name, and max clusters. `.env` is loaded by `main.main` for provider credentials. `settings.py` does not read `LLM_MODEL` or `LLM_FAST_MODEL`, despite stale README/SETTINGS prose claiming those environment overrides; use YAML, CLI, or `configurable` values.

## Important YAML sections

- `models.model` is used for taxonomy generation, update, review, selection, and merge adjudication; `models.fast_llm` is used for summarization, open coding, saturation checks, and labeling. `models.embedding` supports value consolidation and visualization and currently accepts `openai/<model>` or `ollama/<model>`.
- `pipeline.max_runs`, `sample_size`, `batch_size`, and `random_seed` control corpus limiting, sampling, minibatches, and reproducibility.
- `taxonomy` controls name, use case, cluster limits/lengths, `saturation_streak_threshold`, `value_merge_distance_threshold`, `value_merge_borderline_band`, and `consolidate_values`.
- `summarization` controls skip, summary lengths, and `max_concurrency`; that concurrency value also bounds open coding and labeling.
- `labeling` controls `fallback_category` and `review_sample_size`.
- `output` controls display limits, output directory, and graph filename.
- `visualization.enabled`, `every_iteration`, `dimensions`, and `output_dir` control optional PCA/biplot chart rendering. Visualization is off by default; merge decisions use full-dimensional embedding distances, not projected coordinates.

The checked-in `config.yaml` currently sets max_runs/sample_size to 0, batch size 10, seed 4, max clusters 8, review sample 15, consolidation enabled, and visualization disabled. The dataclass defaults differ in several values, so documentation and operational checks should distinguish checked-in YAML from fallback defaults.

## Change surface and validation

To add a setting, update the nested dataclass, `_build_*` helper, `Configuration` field and mapping, checked-in YAML, and consuming node/router/CLI. Validate with `python -c "from taxonomy_generator.settings import load_settings; print(load_settings('config.yaml'))"` and a temporary safe YAML file. Model/embedding names are split at the first slash; actual provider credentials and network availability are required only for LLM or embedding runs.