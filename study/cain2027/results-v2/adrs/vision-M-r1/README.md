# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Orchestrated ML pipeline](0002-orchestrated-ml-pipeline.md)
* [Schedule-based retraining trigger](0003-schedule-based-retraining-trigger.md)
* [Offline evaluation pipeline](0004-offline-evaluation-pipeline.md)
* [Progressive release automation with rollback](0005-progressive-release-automation-with-rollback.md)
* [End-to-end reproducible lifecycle governance](0006-end-to-end-reproducible-lifecycle-governance.md)
* [Input and feature-drift monitoring](0007-input-and-feature-drift-monitoring.md)

## Decisions left open

* Device-to-device update transport and integrity when cameras are offline.
* Model format, hardware compatibility, and device rollback mechanics.
* Image retention, privacy, and newly labelled data transfer from production lines.
* Latency, memory, and throughput targets for inference on camera hardware.
* The specific defect-quality metric and acceptance thresholds for promotion.
