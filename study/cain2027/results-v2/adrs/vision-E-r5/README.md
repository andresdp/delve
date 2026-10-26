# Architecture decisions: On-device visual inspection

* [Local service/API based model serving](0001-local-service-api-based-model-serving.md)
* [Model in monolith](0002-model-in-monolith.md)
* [On-schedule trigger](0003-on-schedule-trigger.md)
* [Batch-based learning](0004-batch-based-learning.md)
* [Data version repository](0005-data-version-repository.md)
* [CI/CD pipeline](0006-ci-cd-pipeline.md)
* [Testing trained model quality](0007-testing-trained-model-quality.md)
* [Rollback to previous model version](0008-rollback-to-previous-model-version.md)

## Decisions left open

* Device update transport, synchronization, and recovery when devices reconnect.
* Model and dataset artifact storage and distribution topology.
* Device hardware capacity, model size, and inference latency targets.
* Security and integrity checks for model artifacts.
* Monitoring and reporting from intermittently connected devices.
