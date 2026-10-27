# Architecture decisions: On-device visual inspection

* [Model as module in modular monolith](0001-model-as-module-in-modular-monolith.md)
* [Local service/API based model serving](0002-local-service-api-based-model-serving.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [CI/CD pipeline](0004-ci-cd-pipeline.md)
* [Rollback to previous model version](0005-rollback-to-previous-model-version.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)
* [Build, test, and deploy models to be served and other system components](0007-build-test-and-deploy-models-to-be-served-and-other-system-c.md)
* [Testing trained model quality](0008-testing-trained-model-quality.md)

## Decisions left open

* How to transfer and stage updates on intermittently connected devices.
* How to store and synchronize newly labelled images.
* Device provisioning, hardware constraints, and fleet management.
* Model artifact security and release authorization.
* Inspection quality metrics and thresholds.
