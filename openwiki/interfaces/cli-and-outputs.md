---
type: interface reference
title: CLI and output contracts
description: Command-line inputs, configuration overrides, Rich execution behavior, graph export, and timestamped JSON result schemas including selected taxonomy output.
tags: [cli, outputs, api]
---

# CLI and output contracts

## Options and execution

`main.py` exposes required `--corpus PATH`; `--config PATH`; `--model PROVIDER/MODEL`; `--fast-model PROVIDER/MODEL`; `--name`; `-k/--max-clusters` (0 means unlimited); `--output DIR`; `--quiet`; feedback options `--feedback` and `--feedback-file`; and taxonomy-file display options including `--iteration`. Standalone `--visualize FILE`, `--report FILE`, `--evaluate TAXONOMY...`, and `--html-report TAXONOMY` modes are mutually exclusive and bypass pipeline execution. `--evaluate` accepts one saved taxonomy for scoring or multiple files for consistency comparison; `--all-iterations` re-scores every saved iteration. `--no-auto-report` opts out of the report automatically generated with `--output`. Corpus input is TXT lines or a JSON array of strings/objects with `content`.

`run` initializes settings, loads the corpus, builds flat `RunnableConfig.configurable` overrides, optionally exports the graph PNG, and streams `graph.astream(..., stream_mode="updates")`. It renders node progress and final Rich views. Non-quiet graph export failures are logged without aborting; `--quiet` suppresses graph export and lowers logging but still renders results. `TokenTracker` reads token usage from response metadata when available.

## Taxonomy views and saved files

The dimension selector adds `selected_clusters` after the full taxonomy iterations. CLI taxonomy display chooses `--iteration` first, then `selected_clusters`, then the last iteration. This makes the selected view suitable for use-case-focused presentation while preserving the full history for inspection. In reusable test mode, `pipeline.taxonomy_input` seeds the selected view by default, labels a new corpus against frozen dimensions, and writes `delta_summary` after new-value aggregation.

With `--output`, the directory is created and sanitized taxonomy name plus timestamp are used in `{documents|taxonomy|messages|clusters}_YYYYMMDD_HHMMSS.json` filenames:

- Documents: `{taxonomy_name, documents[]}` with `id`, `content`, `summary`, `explanation`, `category`, and `score`.
- Taxonomy: `{taxonomy_name, iterations[]}` with explanations and cluster objects; the full iteration history is preserved, and `selected_clusters` is included when produced.
- Messages: `{taxonomy_name, messages[]}` with message type and string content.
- Clusters: `{taxonomy_name, clusters[]}` grouping labeled documents under generated categories when both clusters and documents exist.
- Evaluation: `{taxonomy_name, evaluation or evaluation_history}` scoreboards when evaluation is enabled or standalone `--evaluate` is used.
- Test-mode delta: `delta_summary` lists appended new values and fallback documents in the graph result and serialized state when applicable.

The display tree adds a virtual fallback category when needed and can differ from serialized generated clusters. With `--output`, `main.py` also writes `<taxonomy>_report_<timestamp>.md` through `report_renderer.generate_and_write_report`, unless `--no-auto-report` is set; it may also write a self-contained HTML report through `--html-report` when requested. The report's deterministic diagram/catalog are based on the selected view, while its narrative may require the fast model. Standalone evaluation, report, chart, and HTML behavior is documented in [Taxonomy visualization and grounded-theory reports](reporting-and-visualization.md) and [Taxonomy evaluation and feedback loop](../pipeline/evaluation.md).

Output serialization belongs to `main.py`; state or schema changes must update these serializers and Rich views together. Validate parser/help and local serialization without network; full pipeline execution and narrative/embedding rendering are conditional on external LLM and embedding providers.