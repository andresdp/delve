# Architecture decisions: Retail demand forecasting

* [Reproduce forecasts from past data](0001-reproduce-forecasts-from-past-data.md)
* [Batch-based learning](0002-batch-based-learning.md)
* [Automate model and component delivery](0003-automate-model-and-component-delivery.md)
* [Test changes before production](0004-test-changes-before-production.md)
* [Trigger the weekly forecast pipeline](0005-trigger-the-weekly-forecast-pipeline.md)
* [Monitor production forecasts](0006-monitor-production-forecasts.md)

## Decisions left open

* Forecast serving interface and consumers
* Data ingestion and source quality controls
* Forecast output storage and access
* Release rollback or promotion policy
* Definition of model quality thresholds
* Failure alerting, recovery, and run ownership
* Data retention and access controls
