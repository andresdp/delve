# Architecture decisions: Retail demand forecasting

* [data ingestion mechanism](0001-data-ingestion-mechanism.md)
* [workflow execution coordination](0002-workflow-execution-coordination.md)
* [ml artifact and lifecycle versioning](0003-ml-artifact-and-lifecycle-versioning.md)
* [release automation](0004-release-automation.md)
* [candidate evaluation and regression checks](0005-candidate-evaluation-and-regression-checks.md)

## Not grounded in the design space

* Forecast error metric, threshold values, and store/product-level acceptance policy.
* How source data and labels are retained for historical replay, including correction handling.
* Model family, training/update cadence, and forecast-serving or delivery interface.
* Monitoring responsibilities and response process when actual demand diverges from forecasts.
