# Architecture decisions: Retail demand forecasting

* [Data ingestion mechanism](0001-data-ingestion-mechanism.md)
* [ML workflow execution coordination](0002-ml-workflow-execution-coordination.md)
* [Model evaluation and regression strategy](0003-model-evaluation-and-regression-strategy.md)
* [ML release automation](0004-ml-release-automation.md)
* [Prediction serving mode](0005-prediction-serving-mode.md)
* [ML artifact and lifecycle versioning](0006-ml-artifact-and-lifecycle-versioning.md)

## Decisions left open

* How store and product history is retained and corrected for past-week reruns.
* Forecast data schema, publication destination, and consumer contract.
* The exact demand model family, forecast horizon, and error metrics.
* Operational alerting and recovery procedures for a missed or failed weekly run.
