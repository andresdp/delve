# Architecture decisions: On-device visual inspection

* [Serve predictions locally on each line](0001-serve-predictions-locally-on-each-line.md)
* [Train models in batches](0002-train-models-in-batches.md)
* [Automate model building, evaluation and validation](0003-automate-model-building-evaluation-and-validation.md)
* [Trigger retraining weekly](0004-trigger-retraining-weekly.md)
* [Version training data](0005-version-training-data.md)
* [Automate model delivery](0006-automate-model-delivery.md)
* [Retain a previous model for rollback](0007-retain-a-previous-model-for-rollback.md)
* [Test trained model quality before release](0008-test-trained-model-quality-before-release.md)

## Decisions left open

* How devices receive staged model updates while offline and reconcile when connectivity returns.
* Device identity, update authentication and model integrity protection.
* Target latency, camera throughput, device hardware and storage limits.
* How production predictions and defect labels are collected for monitoring and future training.
