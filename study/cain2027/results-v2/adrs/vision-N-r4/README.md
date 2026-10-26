# Architecture decisions: On-device visual inspection

* [Run inference on-device](0001-run-inference-on-device.md)
* [Distribute weekly models for local installation](0002-distribute-weekly-models-for-local-installation.md)
* [Train weekly from a versioned image dataset](0003-train-weekly-from-a-versioned-image-dataset.md)
* [Validate models before fleet rollout](0004-validate-models-before-fleet-rollout.md)

## Decisions left open

* Target inference latency and device hardware capabilities.
* Defect classes, acceptable false-positive and false-negative rates, and validation metrics.
* Image retention, labeling workflow, and dataset access controls.
* Model format, runtime, package transport, and device identity/security.
* Fleet size, connectivity patterns, update scheduling, rollback mechanism, and deployment success monitoring.
