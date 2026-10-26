# Architecture decisions: Retail demand forecasting

* [prioritize the system requirements](0001-prioritize-the-system-requirements.md)
* [run forecasts as a weekly batch](0002-run-forecasts-as-a-weekly-batch.md)
* [preserve inputs and artifacts for historical reruns](0003-preserve-inputs-and-artifacts-for-historical-reruns.md)
* [promote model changes through a release gate](0004-promote-model-changes-through-a-release-gate.md)
* [keep one pipeline owned end to end](0005-keep-one-pipeline-owned-end-to-end.md)

## Not grounded in the design space

* Input data sources, quality checks, and late-arriving data policy
* Forecast accuracy metrics and model promotion thresholds
* Forecast consumers, delivery interface, and availability targets
* Compute, storage, orchestration, and retention constraints
* Backfill scope, concurrency, and recovery objectives
