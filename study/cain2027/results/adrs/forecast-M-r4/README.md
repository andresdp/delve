# Architecture decisions: Retail demand forecasting

* [Use ETL-based feature ingestion for weekly demand data](0001-use-etl-based-feature-ingestion-for-weekly-demand-data.md)
* [Score forecasts through scheduled batch prediction](0002-score-forecasts-through-scheduled-batch-prediction.md)
* [Version pipeline definitions and experiments together](0003-version-pipeline-definitions-and-experiments-together.md)
* [Use commit-triggered staged release automation](0004-use-commit-triggered-staged-release-automation.md)
* [Gate model promotion with offline evaluation](0005-gate-model-promotion-with-offline-evaluation.md)
* [Orchestrate the weekly ML workflow as a repeatable pipeline](0006-orchestrate-the-weekly-ml-workflow-as-a-repeatable-pipeline.md)

## Decisions left open

* Exact demand model family and feature set
* Forecast quality metric and promotion threshold
* Storage and retention policy for historical inputs and forecast outputs
* Weekly schedule, failure recovery, and operational ownership
