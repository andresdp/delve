# Architecture decisions: On-device visual inspection

* [Local service/API based model serving](0001-local-service-api-based-model-serving.md)
* [Model as module in modular monolith](0002-model-as-module-in-modular-monolith.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [Data version repository](0004-data-version-repository.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [On-schedule trigger](0006-on-schedule-trigger.md)
* [Rollback to previous model version](0007-rollback-to-previous-model-version.md)
* [Shared data store](0008-shared-data-store.md)
* [Model performance monitoring](0009-model-performance-monitoring.md)

## Decisions left open

* How devices receive model packages while offline, including connectivity windows, transfer security, and rollout coordination.
* Device hardware, model runtime, latency target, and local resource limits.
* What prediction-quality metrics and acceptance thresholds gate a release.
* How devices record and later transfer inspection data and monitoring results.
* How training data is labelled, stored, and synchronized from production sites.
