# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Schedule-based retraining trigger](0002-schedule-based-retraining-trigger.md)
* [Offline evaluation pipeline](0003-offline-evaluation-pipeline.md)
* [Progressive release automation with rollback](0004-progressive-release-automation-with-rollback.md)

## Decisions left open

* How devices exchange model packages when network access is unavailable.
* Image and label storage, retention, and transfer to the training environment.
* Training compute and workflow coordination for the weekly cycle.
* Model family and resource fit for the camera hardware.
* Device fleet management, update authentication, and recovery protocol.
