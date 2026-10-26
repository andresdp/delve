# Architecture decisions: On-device visual inspection

* [Model in monolith](0001-model-in-monolith.md)
* [Local service/API based model serving](0002-local-service-api-based-model-serving.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [On-schedule trigger](0004-on-schedule-trigger.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [Rollback to previous model version](0006-rollback-to-previous-model-version.md)
* [Monitoring or logging data and predictions](0007-monitoring-or-logging-data-and-predictions.md)

## Decisions left open

* Device update transport, fleet targeting, and offline package synchronization.
* Camera hardware sizing, model runtime, and inference latency targets.
* Image labelling workflow, dataset governance, and label quality controls.
* Model acceptance thresholds and production release gates.
* Security, access control, and protection of stored images and logs.
