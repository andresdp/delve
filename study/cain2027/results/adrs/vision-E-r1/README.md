# Architecture decisions: On-device visual inspection

* [Serve predictions through a local device API](0001-serve-predictions-through-a-local-device-api.md)
* [Use deployment scripts for weekly model releases](0002-use-deployment-scripts-for-weekly-model-releases.md)
* [Keep a rollback path for deployed model updates](0003-keep-a-rollback-path-for-deployed-model-updates.md)
* [Schedule retraining weekly as a batch job](0004-schedule-retraining-weekly-as-a-batch-job.md)
* [Trigger retraining on a weekly schedule](0005-trigger-retraining-on-a-weekly-schedule.md)

## Decisions left open

* How to securely distribute and install model updates on devices that are offline.
* How devices buffer images or predictions while disconnected, and when they synchronize.
* How to monitor device health and model quality when telemetry cannot be sent continuously.
* How to manage image labelling and the training data pipeline.
* How to define acceptance criteria and testing before a model is released.
* How to provision and manage device hardware and runtime resources.
