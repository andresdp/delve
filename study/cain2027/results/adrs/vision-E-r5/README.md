# Architecture decisions: On-device visual inspection

* [Embed the model as a module in the camera application](0001-embed-the-model-as-a-module-in-the-camera-application.md)
* [Serve predictions through a local API](0002-serve-predictions-through-a-local-api.md)
* [Automate model delivery with a CI/CD pipeline](0003-automate-model-delivery-with-a-ci-cd-pipeline.md)
* [Keep rollback to the previous model version](0004-keep-rollback-to-the-previous-model-version.md)
* [Version training data in a data version repository](0005-version-training-data-in-a-data-version-repository.md)
* [Retrain on a weekly schedule using batch learning](0006-retrain-on-a-weekly-schedule-using-batch-learning.md)

## Decisions left open

* How to transfer and stage model artifacts across intermittently connected devices, including fleet rollout and update recovery.
* What image retention, privacy, and security controls apply to production and training data.
* What quality gates and tests should block a model release.
* What production monitoring and alerting should operate when devices are offline.
