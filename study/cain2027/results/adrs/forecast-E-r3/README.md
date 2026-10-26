# Architecture decisions: Retail demand forecasting

* [Batch-based data processing](0001-batch-based-data-processing.md)
* [Precompute serving](0002-precompute-serving.md)
* [Data version repository](0003-data-version-repository.md)
* [Scheduled data and model building pipelines](0004-scheduled-data-and-model-building-pipelines.md)
* [Batch-based learning](0005-batch-based-learning.md)
* [Train, validate, and select model candidates](0006-train-validate-and-select-model-candidates.md)
* [Build, test, and deploy ML pipelines and components](0007-build-test-and-deploy-ml-pipelines-and-components.md)
* [Test feature logic, pipeline components, and trained model quality](0008-test-feature-logic-pipeline-components-and-trained-model-qua.md)
* [Rollback to previous model version](0009-rollback-to-previous-model-version.md)
* [Monitor model performance and log data and predictions](0010-monitor-model-performance-and-log-data-and-predictions.md)
* [Manual model adjustment](0011-manual-model-adjustment.md)

## Decisions left open

* Forecast consumers and output interface
* Storage and retention of forecast artifacts
* Feature and label definitions for store-product demand
* Forecast quality metrics and promotion thresholds
* Ownership and alerting for failed weekly runs
* Access control and data privacy
* Recovery time and retention targets
