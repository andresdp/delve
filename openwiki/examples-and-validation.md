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

Automated unit tests are present under `tests/unit_tests/`; checked-in outputs are examples, not tests. The suite covers corpus building, schemas, prompt content/provenance, routing and saturation, value aggregation/consolidation, evaluation metrics/scoreboards, reusable taxonomy seed views, labeling/evidence fixes, and Markdown/HTML reports. Source-level invariants to preserve include: empty corpus raises `ValueError`; non-positive batch size raises `ValueError`; routing terminates when revisions reach minibatch count; test mode freezes seed dimensions before value aggregation; evaluation is fail-soft and observe-only; labeling rejects missing clusters; summary/label concurrency is bounded; and output clusters are omitted when no final taxonomy/documents exist.

Non-network checks (with dependencies installed) include:

```bash
python -c "import taxonomy_generator; print(taxonomy_generator.__all__)"
python -c "import taxonomy_generator.prompts; from taxonomy_generator.graph import graph; print(graph)"
python main.py --help
python -c "from taxonomy_generator.settings import load_settings; print(load_settings('config.yaml'))"
python -m pytest tests/unit_tests/test_taxonomy_evaluator.py tests/unit_tests/test_seed_view.py tests/unit_tests/test_html_report_cli.py -q
```

Also check `strings_to_docs`, `docs_from_dicts`, `_create_batches`, safe `load_corpus` samples, package discovery/console metadata, and the focused suites named above. The `Makefile` advertises `make test`/`extended_tests` pytest targets under `tests/unit_tests/`, plus Ruff/mypy `lint` and `lint_tests` targets; use the affected pytest files directly for narrow validation and reserve full lint/root test targets for deliberate broader checks. The `.github/workflows/openwiki-update.yml` is documentation automation, not part of Delve's taxonomy runtime. Provider-backed judge, generation, embedding, and visualization smoke runs are conditional, expensive/networked validation rather than focused checks.

## Backlog

- Restore or update the missing architecture-decision source/config files, with a source anchor in `EXAMPLES.md` and `examples/prepare_decisions_corpus.py`, before claiming that workflow is runnable.
