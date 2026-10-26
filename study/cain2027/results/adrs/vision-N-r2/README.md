# Architecture decisions: On-device visual inspection

* [Run inference on the production-line devices](0001-run-inference-on-the-production-line-devices.md)
* [Retrain models on a weekly batch cadence](0002-retrain-models-on-a-weekly-batch-cadence.md)
* [Distribute model updates to devices](0003-distribute-model-updates-to-devices.md)

## Decisions left open

* Where newly labelled images are collected, stored, and transferred from production lines.
* Training compute, framework, and execution environment.
* Model validation and release criteria before deployment.
* Model artifact format and device inference runtime.
* Update authentication, integrity checks, staged rollout, and rollback behavior.
* Device hardware and supported operating systems.
* Inspection result storage, alerting, and retention requirements.
