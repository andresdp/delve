# Architecture decisions: On-device visual inspection

* [Use a local prediction service for on-device inspection](0001-use-a-local-prediction-service-for-on-device-inspection.md)
* [Train models in weekly batches](0002-train-models-in-weekly-batches.md)
* [Use deployment scripts for weekly model delivery](0003-use-deployment-scripts-for-weekly-model-delivery.md)
* [Keep a rollback path for deployed models](0004-keep-a-rollback-path-for-deployed-models.md)
* [Version labelled training data in a data version repository](0005-version-labelled-training-data-in-a-data-version-repository.md)
* [Store shared training data in a shared data store](0006-store-shared-training-data-in-a-shared-data-store.md)
* [Test model quality and the deployed prediction API](0007-test-model-quality-and-the-deployed-prediction-api.md)

## Decisions left open

* Device fleet management and rollout coordination across cameras.
* How devices receive updates while offline and reconcile when connectivity returns.
* Model artifact format, compatibility checks, and device resource limits.
* Image retention, privacy, security, and access control.
* Monitoring and alerting for camera health, predictions, and model performance.
* How newly labelled images are collected and validated.
