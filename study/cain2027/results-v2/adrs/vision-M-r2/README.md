# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should weekly model releases be deployed](0002-how-should-weekly-model-releases-be-deployed.md)
* [how should training and model artifacts be versioned](0003-how-should-training-and-model-artifacts-be-versioned.md)
* [what should trigger model retraining](0004-what-should-trigger-model-retraining.md)

## Not grounded in the design space

* How cameras receive model updates while offline, including synchronization and retry behavior.
* How inference behaves during a partially applied update or failed model load.
* Model evaluation and promotion thresholds for defect detection.
* Device identity, access control, and update security.
* Whether drift monitoring should also trigger retraining between weekly runs.
