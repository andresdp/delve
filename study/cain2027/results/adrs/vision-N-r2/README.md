# Architecture decisions: On-device visual inspection

* [Run defect inference on the production-line devices](0001-run-defect-inference-on-the-production-line-devices.md)
* [Retrain models weekly from newly labelled images](0002-retrain-models-weekly-from-newly-labelled-images.md)
* [Distribute versioned model releases for offline installation](0003-distribute-versioned-model-releases-for-offline-installation.md)
* [Keep the previous model available for rollback](0004-keep-the-previous-model-available-for-rollback.md)

## Decisions left open

* Camera hardware, device operating systems, and available compute
* Defect classes, accuracy targets, and inspection latency limits
* Image retention, privacy, and labelling workflow
* Update transport, device identity, and release authorization
* Model validation gates and rollout success criteria
* Monitoring and reporting requirements for offline devices
