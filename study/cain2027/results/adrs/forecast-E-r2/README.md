# Architecture decisions: Retail demand forecasting

* [Batch-based data processing](0001-batch-based-data-processing.md)
* [Model building pipeline](0002-model-building-pipeline.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [Data version repository](0004-data-version-repository.md)
* [On-schedule trigger](0005-on-schedule-trigger.md)
* [Build, test, and deploy models to be served and other system components](0006-build-test-and-deploy-models-to-be-served-and-other-system-c.md)
* [Rollback to previous model version](0007-rollback-to-previous-model-version.md)
* [Model performance monitoring](0008-model-performance-monitoring.md)

## Decisions left open

* Forecast error metrics, acceptance thresholds, and promotion gates.
* Forecast storage, delivery, and consumer interface.
* Retention period and exact mechanism for historical input snapshots.
