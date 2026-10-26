# Architecture decisions: On-device visual inspection

* [run inference on device](0001-run-inference-on-device.md)
* [distribute weekly models for local installation](0002-distribute-weekly-models-for-local-installation.md)
* [train weekly from a versioned image dataset](0003-train-weekly-from-a-versioned-image-dataset.md)
* [validate models before fleet rollout](0004-validate-models-before-fleet-rollout.md)

## Not grounded in the design space

* Target inference latency and device hardware capabilities.
* Defect classes, acceptable false-positive and false-negative rates, and validation metrics.
* Image retention, labeling workflow, and dataset access controls.
* Model format, runtime, package transport, and device identity/security.
* Fleet size, connectivity patterns, update scheduling, rollback mechanism, and deployment success monitoring.
