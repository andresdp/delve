# Architecture decisions: On-device visual inspection

* [Use a CI/CD pipeline for weekly model delivery](0001-use-a-ci-cd-pipeline-for-weekly-model-delivery.md)
* [Deploy one production model with rollback](0002-deploy-one-production-model-with-rollback.md)
* [Track training data in a data version repository](0003-track-training-data-in-a-data-version-repository.md)
* [Train models in weekly batches](0004-train-models-in-weekly-batches.md)
* [Run inference through a local device service](0005-run-inference-through-a-local-device-service.md)
* [Monitor model performance in production](0006-monitor-model-performance-in-production.md)
* [Use human review to adjust models](0007-use-human-review-to-adjust-models.md)

## Decisions left open

* Device enrollment, identity, and secure model transfer while offline.
* Device hardware sizing and model optimization.
* How predictions and inspection images are buffered or synchronized after connectivity returns.
* Defect labels, acceptance thresholds, and release quality gates.
* Model artifact signing and device-side integrity verification.
