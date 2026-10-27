# Architecture decisions: On-device visual inspection

* [Embed the inspection model in a modular application](0001-embed-the-inspection-model-in-a-modular-application.md)
* [Store training images in a shared data store](0002-store-training-images-in-a-shared-data-store.md)
* [Ingest labelled images in batches](0003-ingest-labelled-images-in-batches.md)
* [Automate model delivery with a CI/CD pipeline](0004-automate-model-delivery-with-a-ci-cd-pipeline.md)
* [Keep a rollback path for deployed model versions](0005-keep-a-rollback-path-for-deployed-model-versions.md)
* [Version training data in a data version repository](0006-version-training-data-in-a-data-version-repository.md)
* [Trigger retraining on a weekly schedule](0007-trigger-retraining-on-a-weekly-schedule.md)
* [Build and validate models in an automated pipeline](0008-build-and-validate-models-in-an-automated-pipeline.md)
* [Use batch-based model learning](0009-use-batch-based-model-learning.md)

## Decisions left open

* How to distribute model packages to disconnected cameras and synchronize updates when they reconnect.
* How to handle camera connectivity, package integrity, staged rollout, and fleet-level deployment status.
* Which image-quality and defect metrics determine model acceptance and rollback.
* How to secure and retain production images and labelled data.
