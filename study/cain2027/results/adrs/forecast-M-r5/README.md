# Architecture decisions: Retail demand forecasting

* [Use an orchestrated pipeline for weekly model workflows](0001-use-an-orchestrated-pipeline-for-weekly-model-workflows.md)
* [Track complete lifecycle lineage for reproducible forecasts](0002-track-complete-lifecycle-lineage-for-reproducible-forecasts.md)
* [Promote model changes through staged automated releases](0003-promote-model-changes-through-staged-automated-releases.md)
* [Evaluate candidates against held-out historical data](0004-evaluate-candidates-against-held-out-historical-data.md)
* [Generate weekly forecasts with scheduled batch scoring](0005-generate-weekly-forecasts-with-scheduled-batch-scoring.md)
* [Monitor feature drift after deployment](0006-monitor-feature-drift-after-deployment.md)

## Decisions left open

* Data ingestion mechanism and source-system integration; the checked workflow point warns this decision is required, but the brief does not identify the data sources or delivery mechanism.
* Forecast model family, training and tuning approach, and demand-specific evaluation metrics.
* Data retention period and access controls for historical inputs and forecast runs.
* Alert ownership, response times, and whether drift should trigger automatic or human-approved retraining.
