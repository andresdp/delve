# Architecture decisions: On-device visual inspection

* [Model as module in modular monolith](0001-model-as-module-in-modular-monolith.md)
* [Local service/API based model serving](0002-local-service-api-based-model-serving.md)
* [On-schedule trigger with batch-based learning](0003-on-schedule-trigger-with-batch-based-learning.md)
* [CI/CD pipeline](0004-ci-cd-pipeline.md)
* [Rollback to previous model version](0005-rollback-to-previous-model-version.md)
* [Data version repository](0006-data-version-repository.md)
* [Testing trained model quality](0007-testing-trained-model-quality.md)
* [Monitoring or logging data and predictions](0008-monitoring-or-logging-data-and-predictions.md)

## Decisions left open

* Device communication and artifact synchronization during intermittent connectivity.
* Model artifact security, integrity, and device authentication.
* Image retention and privacy requirements.
* Evaluation metric and minimum acceptable defect-detection quality.
