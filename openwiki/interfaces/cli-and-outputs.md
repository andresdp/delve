---
type: interface reference
title: CLI and output contracts
description: Command-line inputs, configuration overrides, Rich execution behavior, graph export, and timestamped JSON result schemas.
tags: [cli, outputs, api]
---

# CLI and output contracts

## Options and input

`main.py` groups options as follows: required `--corpus PATH`; `--config PATH`; `--model PROVIDER/MODEL`; `--fast-model PROVIDER/MODEL`; `--name`; `-k/--max-clusters` (0 means unlimited); `--output DIR`; and `--quiet`. `--corpus` accepts text lines or a JSON array of strings/objects with `content`. Missing `--corpus` exits with status 1; file and JSON parsing errors propagate after logging.

CLI overrides are converted to flat `RunnableConfig.configurable` values for model, fast model, taxonomy name, and max clusters. Settings loading and precedence are detailed in [Configuration and settings](../configuration/settings.md).

## Execution behavior

`main.main` calls `load_dotenv`, parses arguments, and configures logging. `run` calls `init_settings`, loads the corpus, builds CLI `configurable` overrides, resolves an effective `Configuration`, optionally exports the compiled graph PNG, then streams `graph.astream(..., stream_mode="updates")`; each node update is rendered before final taxonomy/document/tree/message panels and optional serialization. Non-quiet runs attempt to export `graph.png` (or configured `graph_filename`) to `--output` or the default output directory; export failures are logged and do not abort. `--quiet` changes logging to WARNING and suppresses graph export, but still shows Rich result panels and step progress.

`TokenTracker.on_llm_end` checks each generation's message `response_metadata` first and `generation_info` second, looking for `token_usage` or `usage` dictionaries and accumulating total, prompt, and completion counts. Missing or malformed metadata is swallowed with debug logging, so the final report displays `N/A` when no usable counts were observed.

Display limits come from output settings: document table count, per-category tree count, and content preview length. The tree sorts the fallback category last and creates a virtual fallback branch when labeled documents use it but the final taxonomy lacks it.

## Saved JSON files

When `--output` is supplied, the directory is created and filenames use sanitized taxonomy name plus `{documents|taxonomy|messages|clusters}_YYYYMMDD_HHMMSS.json`.

- Documents: `{taxonomy_name, documents[]}` with `id`, `content`, `summary`, `explanation`, `category`, `score`.
- Taxonomy: `{taxonomy_name, iterations[]}`; each iteration has `explanation` and `clusters[]` with `id`, `name`, `description`. The last iteration is final.
- Messages: `{taxonomy_name, messages[]}`; each has message `type` and string `content`.
- Clusters: `{taxonomy_name, clusters[]}`; each cluster has id/name/description and all categorized documents with id/content/score. This file is written only when both clusters and documents exist. Unlike the display tree, serialization does not add a virtual fallback cluster: it serializes only generated clusters, so fallback-labeled documents may not appear under a cluster. Missing generated cluster IDs remain null because the serializer uses `cluster.get("id")`; document score uses an `or` expression in the tree serializer, so a numeric zero can display as missing there.

The display tree groups every document by category, sorts a generated fallback last, and adds a virtual fallback branch when needed. It is therefore not a lossless mirror of the `clusters` JSON. Output serialization is owned by `main.py`, not graph nodes. Changes to state or schemas must update these serializers and the Rich views together. Validate parser/help and serialization with local non-network inputs; a full run invokes external LLMs.
