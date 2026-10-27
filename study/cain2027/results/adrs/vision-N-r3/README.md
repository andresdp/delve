# Architecture decisions: On-device visual inspection

* [Run defect inference on the production-line devices](0001-run-defect-inference-on-the-production-line-devices.md)
* [Distribute retrained models as device updates](0002-distribute-retrained-models-as-device-updates.md)
* [Retrain models in a centralized weekly pipeline](0003-retrain-models-in-a-centralized-weekly-pipeline.md)
* [Track model releases with explicit versions](0004-track-model-releases-with-explicit-versions.md)

## Decisions left open

* Image storage location, retention, and access controls
* Model validation and approval criteria before release
* Device update authentication, integrity checks, and rollback behavior
* Device hardware and inference latency requirements
* Fleet connectivity patterns and update scheduling policy
