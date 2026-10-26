# Architecture decisions: Retail demand forecasting

* [how should the weekly pipeline run](0001-how-should-the-weekly-pipeline-run.md)
* [how should past week forecasts be reproducible](0002-how-should-past-week-forecasts-be-reproducible.md)
* [how should new model ideas reach production](0003-how-should-new-model-ideas-reach-production.md)
* [how should forecasts be published for consumers](0004-how-should-forecasts-be-published-for-consumers.md)

## Not grounded in the design space

* Source systems, data quality rules, and late or corrected data handling.
* Forecast horizon, required accuracy, evaluation metrics, and baseline.
* Infrastructure, orchestration technology, storage platform, and deployment environment.
* Consumer requirements, access controls, and forecast delivery timing.
* Run failure service levels, alerting ownership, and artifact retention period.
