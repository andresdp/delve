# Architecture decisions: Retail demand forecasting

* [data ingestion mechanism](0001-data-ingestion-mechanism.md)
* [ml workflow execution coordination](0002-ml-workflow-execution-coordination.md)
* [model evaluation and regression strategy](0003-model-evaluation-and-regression-strategy.md)
* [ml release automation](0004-ml-release-automation.md)
* [prediction serving mode](0005-prediction-serving-mode.md)
* [ml artifact and lifecycle versioning](0006-ml-artifact-and-lifecycle-versioning.md)

## Not grounded in the design space

* How store and product history is retained and corrected for past-week reruns.
* Forecast data schema, publication destination, and consumer contract.
* The exact demand model family, forecast horizon, and error metrics.
* Operational alerting and recovery procedures for a missed or failed weekly run.
