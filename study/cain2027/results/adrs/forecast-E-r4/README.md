# Architecture decisions: Retail demand forecasting

* [Use batch processing for weekly demand data](0001-use-batch-processing-for-weekly-demand-data.md)
* [Use a data version repository for reproducible forecasts](0002-use-a-data-version-repository-for-reproducible-forecasts.md)
* [Train models in batches for the weekly forecast run](0003-train-models-in-batches-for-the-weekly-forecast-run.md)
* [Use CI/CD automation to deliver model changes](0004-use-ci-cd-automation-to-deliver-model-changes.md)
* [Test trained model quality before release](0005-test-trained-model-quality-before-release.md)
* [Keep a rollback path for production models](0006-keep-a-rollback-path-for-production-models.md)

## Decisions left open

* How store and product data are ingested and validated.
* How forecast results are delivered to users or downstream systems.
* Forecast accuracy metrics, acceptance thresholds, and evaluation windows.
* Run scheduling, failure recovery, and operational ownership details.
