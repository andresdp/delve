# Architecture decisions: On-device visual inspection

* [On-device inference](0001-on-device-inference.md)
* [Staged update service](0002-staged-update-service.md)
* [Central batch training](0003-central-batch-training.md)
* [Versioned rollout with rollback](0004-versioned-rollout-with-rollback.md)

## Decisions left open

* Camera and device hardware, inference runtime, and compute limits.
* Image volume, retention, privacy constraints, and the process for moving newly labelled images to training.
* Defect acceptance thresholds, model evaluation criteria, and who approves weekly releases.
* Required update freshness, offline duration, connectivity patterns, and device identity or authentication.
* Expected inspection throughput, latency, availability, and behavior when inference fails.
