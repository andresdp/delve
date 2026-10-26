# Architecture decisions: Retail demand forecasting

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data version repository](0003-data-version-repository.md)
* [On-schedule trigger](0004-on-schedule-trigger.md)
* [Model building pipeline](0005-model-building-pipeline.md)
* [Batch-based learning](0006-batch-based-learning.md)
* [CI/CD pipeline](0007-ci-cd-pipeline.md)
* [Build, test, and deploy models to be served and other system components](0008-build-test-and-deploy-models-to-be-served-and-other-system-c.md)
* [Model performance monitoring](0009-model-performance-monitoring.md)
* [Testing trained model quality](0010-testing-trained-model-quality.md)

## Decisions left open

* Forecasting model family and feature design.
* Forecast quality metric and acceptance thresholds.
* Prediction serving interface and forecast consumers.
* Retention policy and storage location for versioned data and model artifacts.
* Rollback and recovery procedure for a failed weekly run.
