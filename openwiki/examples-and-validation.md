---
type: examples and validation
title: Examples and repository validation
description: Corpus examples, preparation workflows, checked-in generated artifacts, known missing inputs, and deterministic validation boundaries.
tags: [examples, validation, operations]
---

# Examples and repository validation

## Inventory and provenance

The repository includes `examples/product_reviews.json` and `examples/customer_support.txt` as direct corpus inputs. `examples/campus-bike/`, `examples/das-p1-2023/`, and `examples/pharmacy-food/` contain architecture-decision JSON inputs, per-example YAML configs, taxonomy text, graph PNGs, and timestamped taxonomy/document/message/cluster/report artifacts. The root `output/` similarly contains timestamped `architecture-decisions` and `reviews` result families. Treat all timestamped JSON/PNG/Markdown files as generated samples, not authoritative input or tests. `EXAMPLES.md` describes a product-review run and an architecture-decision run.

The architecture-decision workflow documents `examples/decisions_results.json` and `examples/config_decisions.yaml`, but those files are not present in the inventory. `examples/prepare_decisions_corpus.py` expects the missing `decisions_results.json`, so running it currently fails at its source-input boundary rather than proving the pipeline. This is a known backlog item for restoring the documented example, not a reason to invent a replacement corpus.

## Commands and expected behavior

- `python main.py --corpus examples/product_reviews.json --quiet --output output/` exercises JSON input, full graph flow, and four output families when provider configuration is available.
- `python main.py --corpus examples/customer_support.txt ...` exercises one-document-per-line text input.
- `python examples/prepare_decisions_corpus.py` is expected to fail until its documented source JSON is restored; if restored, pair it with `examples/config_decisions.yaml` and the command in `EXAMPLES.md`.

## Validation contract

No automated unit, integration, or end-to-end test files were found. Checked-in outputs are examples, not tests. Source-level invariants to manually preserve include: empty corpus raises `ValueError`; non-positive batch size raises `ValueError`; routing terminates when revisions reach minibatch count; labeling rejects missing clusters; summary/label concurrency is bounded; and output clusters are omitted when no final taxonomy/documents exist.

Non-network checks (with dependencies installed) include:

```bash
python -c "import taxonomy_generator; print(taxonomy_generator.__all__)"
python -c "import taxonomy_generator.prompts; from taxonomy_generator.graph import graph; print(graph)"
python main.py --help
python -c "from taxonomy_generator.settings import load_settings; print(load_settings('config.yaml'))"
```

Also check `strings_to_docs`, `docs_from_dicts`, `_create_batches`, safe `load_corpus` samples, package discovery/console metadata, and the expected missing-input failure of the preparation script. `prepare_decisions_corpus.py` opens `examples/decisions_results.json`, expects a list of objects with `decision`, `pattern`, and `rationale`, skips records missing `decision`, joins those fields into one text string, and writes `examples/architecture_decisions.json` as a JSON array. The `Makefile` advertises `make test`/`extended_tests` pytest targets under `tests/unit_tests/`, plus Ruff/mypy `lint` and `lint_tests` targets; that test directory/files were not found, so pytest targets are unavailable/stale rather than evidence of coverage. The `.github/workflows/openwiki-update.yml` is documentation automation: `workflow_dispatch` and daily `0 8 * * *` scheduling run Ubuntu with pinned checkout/setup actions, `fetch-depth: 0`, Node 22, global OpenWiki/Mermaid/jsdom installation, then `openwiki code --update --print` with provider/LangSmith environment values and secrets; `peter-evans/create-pull-request` writes `openwiki`, agent docs, and workflow changes to branch `openwiki/update`. It is not part of Delve's taxonomy runtime. Provider-backed smoke runs are conditional, expensive/networked validation rather than focused checks.

## Backlog

- Restore or update the missing architecture-decision source/config files, with a source anchor in `EXAMPLES.md` and `examples/prepare_decisions_corpus.py`, before claiming that workflow is runnable.
