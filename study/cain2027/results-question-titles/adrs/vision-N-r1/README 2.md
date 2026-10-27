# Architecture decisions: On-device visual inspection

* [where should defect inference run](0001-where-should-defect-inference-run.md)
* [how should weekly models reach devices](0002-how-should-weekly-models-reach-devices.md)
* [how should training run](0003-how-should-training-run.md)
* [how should model updates be protected](0004-how-should-model-updates-be-protected.md)

## Not grounded in the design space

* Camera and device hardware, inference runtime, and compute limits.
* Image volume, retention, privacy constraints, and the process for moving newly labelled images to training.
* Defect acceptance thresholds, model evaluation criteria, and who approves weekly releases.
* Required update freshness, offline duration, connectivity patterns, and device identity or authentication.
* Expected inspection throughput, latency, availability, and behavior when inference fails.
