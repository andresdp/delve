# Architecture decisions: On-device visual inspection

* [Run inspection inference on the production-line devices](0001-run-inspection-inference-on-the-production-line-devices.md)
* [Scale weekly training vertically](0002-scale-weekly-training-vertically.md)
* [Trigger retraining on a weekly schedule](0003-trigger-retraining-on-a-weekly-schedule.md)
* [Release model updates through staged automation](0004-release-model-updates-through-staged-automation.md)

## Decisions left open

* Camera and device hardware requirements, including compute, memory, and supported model formats.
* Image and label storage, retention, access controls, and data lineage.
* Model quality thresholds and pre-release validation criteria.
* Device update protocol, rollout pacing, rollback behavior, and recovery for devices offline during updates.
* Production monitoring signals and how inspection errors are detected between weekly retraining runs.
