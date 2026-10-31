# Architecture decisions: On-device visual inspection

* [Batch-based learning](0001-batch-based-learning.md)
* [Model building pipeline](0002-model-building-pipeline.md)
* [Data version repository](0003-data-version-repository.md)
* [Local service/API based model serving](0004-local-service-api-based-model-serving.md)
* [Rollback to previous model version](0005-rollback-to-previous-model-version.md)
* [Build and Deployment scripts](0006-build-and-deployment-scripts.md)
* [Testing trained model quality](0007-testing-trained-model-quality.md)
* [Monitoring or logging data and predictions](0008-monitoring-or-logging-data-and-predictions.md)

## Decisions left open

* How to package, authenticate, and securely deliver model updates to devices.
* How devices stage updates, verify them, and resume safely after interrupted connectivity.
* How to measure defect-detection quality and set release thresholds.
* How to handle camera calibration, image drift, and production-line changes.
* Device hardware, runtime, storage, and compute constraints.
