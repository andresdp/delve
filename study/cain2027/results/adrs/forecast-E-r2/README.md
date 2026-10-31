# Architecture decisions: Retail demand forecasting

* [Version forecasting inputs in a data version repository](0001-version-forecasting-inputs-in-a-data-version-repository.md)
* [Process weekly demand data in batches](0002-process-weekly-demand-data-in-batches.md)
* [Trigger forecasts on a schedule](0003-trigger-forecasts-on-a-schedule.md)
* [Use a CI/CD pipeline for model and system releases](0004-use-a-ci-cd-pipeline-for-model-and-system-releases.md)
* [Train forecasting models with batch learning](0005-train-forecasting-models-with-batch-learning.md)
* [Write scheduled forecasts to data storage](0006-write-scheduled-forecasts-to-data-storage.md)
* [Keep a previous model version available for rollback](0007-keep-a-previous-model-version-available-for-rollback.md)
* [Automatically build, test, and deploy models and system components](0008-automatically-build-test-and-deploy-models-and-system-compon.md)
* [Test model quality before release](0009-test-model-quality-before-release.md)
* [Monitor model performance and prediction records](0010-monitor-model-performance-and-prediction-records.md)

## Decisions left open

* Forecast quality metrics, thresholds, and evaluation windows.
* Input data schemas, source systems, late-arriving data, and correction policy.
* Storage technology, forecast consumers, access control, and retention requirements.
* Schedule timing, run failure recovery, and alert ownership.
* Model family, feature design, and forecasting horizon.
* Data version repository and model artifact format, retention, and linkage details.
