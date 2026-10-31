# Architecture decisions: Retail demand forecasting

* [Run demand forecasting as a weekly batch pipeline](0001-run-demand-forecasting-as-a-weekly-batch-pipeline.md)
* [Version inputs and artifacts to reproduce forecasts for past weeks](0002-version-inputs-and-artifacts-to-reproduce-forecasts-for-past.md)
* [Isolate model experiments from the weekly production run](0003-isolate-model-experiments-from-the-weekly-production-run.md)

## Decisions left open

* Forecast horizon and delivery time
* Source systems and data quality requirements
* Forecast accuracy metrics and promotion thresholds
* Serving and forecast consumer interfaces
* Infrastructure, orchestration, and artifact storage choices
* Failure handling, alerting, and recovery targets
