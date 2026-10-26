# Architecture decisions: Retail demand forecasting

* [version input data for reproducible forecasts](0001-version-input-data-for-reproducible-forecasts.md)
* [what to test before accepting a model](0002-what-to-test-before-accepting-a-model.md)
* [how to roll out and recover a model](0003-how-to-roll-out-and-recover-a-model.md)
* [how to trigger the forecast pipeline](0004-how-to-trigger-the-forecast-pipeline.md)
* [automate integration and delivery](0005-automate-integration-and-delivery.md)
* [process weekly demand data in batches](0006-process-weekly-demand-data-in-batches.md)

## Not grounded in the design space

* Choice of forecasting model and training method.
* Forecast artifact storage and retrieval interface.
* Production monitoring signals and thresholds.
* Data ingestion and feature construction specifics.
* Release approval and candidate promotion criteria.
