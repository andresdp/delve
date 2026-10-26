# Architecture decisions: Retail demand forecasting

* [Version input data for reproducible forecasts](0001-version-input-data-for-reproducible-forecasts.md)
* [Testing trained model quality](0002-testing-trained-model-quality.md)
* [Rollback to previous model version](0003-rollback-to-previous-model-version.md)
* [On-schedule trigger](0004-on-schedule-trigger.md)
* [Automate integration and delivery](0005-automate-integration-and-delivery.md)
* [Process weekly demand data in batches](0006-process-weekly-demand-data-in-batches.md)

## Decisions left open

* Choice of forecasting model and training method.
* Forecast artifact storage and retrieval interface.
* Production monitoring signals and thresholds.
* Data ingestion and feature construction specifics.
* Release approval and candidate promotion criteria.
