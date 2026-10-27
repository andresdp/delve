# Architecture decisions: Retail demand forecasting

* [Forecast demand at the store–product–week grain](0001-forecast-demand-at-the-store-product-week-grain.md)
* [Version all forecast inputs and code for historical reproducibility](0002-version-all-forecast-inputs-and-code-for-historical-reproduc.md)
* [Run forecasting as a scheduled, repeatable weekly pipeline](0003-run-forecasting-as-a-scheduled-repeatable-weekly-pipeline.md)
* [Evaluate and promote model changes through a gated workflow](0004-evaluate-and-promote-model-changes-through-a-gated-workflow.md)
* [Keep production forecasts available when a candidate run fails](0005-keep-production-forecasts-available-when-a-candidate-run-fai.md)

## Decisions left open

* Forecast horizon and when each weekly forecast is issued.
* Demand data sources, schemas, and data-quality rules.
* Evaluation metrics, acceptance thresholds, and baseline model.
* Model families, hierarchy or cross-series reconciliation, and cold-start behavior.
* Deployment environment, orchestration and storage technology choices.
* Forecast consumers, delivery interface, and freshness or latency expectations.
* Operational ownership, alerting targets, and recovery-time expectations.
