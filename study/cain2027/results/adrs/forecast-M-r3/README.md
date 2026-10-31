# Architecture decisions: Retail demand forecasting

* [Track complete ML lifecycle state for reproducible forecasts](0001-track-complete-ml-lifecycle-state-for-reproducible-forecasts.md)
* [Orchestrate the weekly ML workflow as a repeatable pipeline](0002-orchestrate-the-weekly-ml-workflow-as-a-repeatable-pipeline.md)
* [Release forecast updates progressively with rollback](0003-release-forecast-updates-progressively-with-rollback.md)
* [Evaluate candidate forecasts offline before promotion](0004-evaluate-candidate-forecasts-offline-before-promotion.md)

## Decisions left open

* Data ingestion mechanism and historical data retention policy.
* Forecasting objective, metric, and evaluation window.
* How forecast outputs are delivered to store and product consumers.
* Production monitoring signals and the response to forecast degradation.
* Compute platform, storage, and deployment environment.
