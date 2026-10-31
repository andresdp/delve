# Architecture decisions: On-device visual inspection

* [Local service/API based model serving](0001-local-service-api-based-model-serving.md)
* [Batch-based learning](0002-batch-based-learning.md)
* [Data version repository](0003-data-version-repository.md)
* [CI/CD pipeline](0004-ci-cd-pipeline.md)
* [Rollback to previous model version](0005-rollback-to-previous-model-version.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)

## Decisions left open

* How to distribute model packages to intermittently connected devices and manage deferred updates.
* How to collect labels and images from devices when network access is unavailable.
* What device-side hardware, model format, and resource limits to target.
* How to test model quality against defect-specific acceptance thresholds.
