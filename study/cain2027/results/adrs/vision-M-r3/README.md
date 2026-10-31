# Architecture decisions: On-device visual inspection

* [Run defect inference on edge devices](0001-run-defect-inference-on-edge-devices.md)
* [Track the full model lifecycle](0002-track-the-full-model-lifecycle.md)
* [Retrain on the weekly schedule](0003-retrain-on-the-weekly-schedule.md)
* [Release model updates progressively with rollback](0004-release-model-updates-progressively-with-rollback.md)

## Decisions left open

* Offline synchronization of newly labeled images to the retraining environment.
* Secure distribution, device inventory, and rollout coordination across the fleet.
* Device hardware limits, model format, and runtime compatibility.
* How to validate defect-detection quality and approve a model before rollout.
