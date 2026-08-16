---
type: configuration reference
title: Configuration and settings resolution
description: YAML-backed immutable settings, runtime overrides, provider configuration, and effective-value caveats.
tags: [configuration, settings, operations]
---

# Configuration and settings resolution

`settings.py` defines frozen nested dataclasses: `ModelSettings`, `PipelineSettings`, `TaxonomySettings`, `SummarizationSettings`, `LabelingSettings`, and `OutputSettings`, composed into `Settings`. `load_settings(config_path)` reads YAML from the supplied path or `config.yaml` in the current working directory; a missing file or missing section/key falls back to dataclass defaults. It does not validate unknown keys.

## Effective precedence

| Priority | Source | Scope |
|---|---|---|
| 1 | `RunnableConfig.configurable` | Any matching flat `Configuration` field; used by graph callers and CLI-built overrides |
| 2 | YAML | All settings mapped by `Configuration._defaults_from_settings` |
| 3 | Python defaults | Missing file/keys |

`main.run` loads settings via `init_settings(args.config)`, then builds configurable overrides for `--model`, `--fast-model`, `--name`, and `--max-clusters` (0 becomes `None`, meaning no cap). `Configuration.from_runnable_config` caches settings at module level; `init_settings` explicitly replaces the cache, while direct callers can otherwise observe the first-loaded settings for the process.

`.env` is loaded by `main.main` for provider credentials. `settings.py` explicitly says tunable settings are YAML-backed and does not read `LLM_MODEL` or `LLM_FAST_MODEL`. Although README/SETTINGS prose claims those environment variables override model names, that behavior is not implemented; use YAML, CLI flags, or `configurable` values instead. Never place credentials in wiki content.

## YAML sections

`Configuration._defaults_from_settings` maps the YAML tree exactly as follows: `models.model -> model`, `models.fast_llm -> fast_llm`; `pipeline.max_runs/sample_size/batch_size/random_seed` retain those names; `taxonomy.name/max_num_clusters/cluster_name_length/cluster_description_length/suggestion_length/explanation_length/use_case` retain names; `summarization.skip -> skip_summarization`, `summary_length -> summary_length`, `explanation_length -> summary_explanation_length`, `max_concurrency -> summary_max_concurrency`; `labeling.fallback_category/review_sample_size` retain names; and all `output` keys retain names. Current `config.yaml` uses max_runs 0, sample_size 0, batch_size 10, random_seed 4, max clusters 8, and review sample 15, while `settings.py` built-ins use batch size 200, random seed None, max clusters None, and review sample None (other defaults are mostly aligned).

`models` selects `model` for taxonomy generation/update/review and `fast_llm` for summary/labeling. `pipeline` controls `max_runs`, `sample_size`, `batch_size`, and `random_seed`. `taxonomy` controls name, use case, cluster/name/description/suggestion/explanation lengths, and optional max clusters. `summarization` controls skip, lengths, and `max_concurrency`; `labeling` controls `fallback_category` and review sample size; `output` controls display limits, default output directory, and graph filename. Settings accept arbitrary YAML types/unknown keys without range or schema validation: negative limits can pass into later node checks, model format is only split when a model is loaded, and concurrency/cluster limits are not validated centrally.

To add a setting, update the nested frozen dataclass, its `_build_*` helper, the `Configuration` field and `_defaults_from_settings` mapping, checked-in YAML/example configs, and the consuming node/router/CLI surface; add a CLI override only when it is intentionally user-facing, then update settings/API documentation and non-network checks.
## Validation and operations

Use `python -c "from taxonomy_generator.settings import load_settings; print(load_settings('config.yaml'))"` and a temporary safe YAML file to check fallback/mapping behavior. `--config` is cwd/path based, not repository-root anchored. Model names must be `provider/model`; `utils.load_chat_model` splits on the first slash and delegates to LangChain `init_chat_model`. Provider credentials and network availability are prerequisites only for actual LLM runs.
