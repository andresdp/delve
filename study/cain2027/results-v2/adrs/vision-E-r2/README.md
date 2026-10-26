# Architecture decisions: On-device visual inspection

* [Model as module in modular monolith](0001-model-as-module-in-modular-monolith.md)
* [Local service/API based model serving](0002-local-service-api-based-model-serving.md)
* [On-schedule trigger with batch-based learning](0003-on-schedule-trigger-with-batch-based-learning.md)
* [Data version repository](0004-data-version-repository.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [Rollback to previous model version](0006-rollback-to-previous-model-version.md)
* [Model performance monitoring](0007-model-performance-monitoring.md)

## Decisions left open

* Offline device update protocol, including package transfer, retries, and fleet rollout strategy.
* Camera hardware sizing, inference latency targets, and resource limits.
* Model acceptance thresholds, defect class metrics, and labeling quality controls.
* Security, authentication, and integrity checks for model artifacts and device updates.
* Retention and privacy rules for production images, predictions, and logs.
