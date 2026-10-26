# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Schedule-based retraining trigger](0002-schedule-based-retraining-trigger.md)
* [Offline evaluation pipeline](0003-offline-evaluation-pipeline.md)
* [Progressive release automation with rollback](0004-progressive-release-automation-with-rollback.md)
* [Orchestrated ML pipeline](0005-orchestrated-ml-pipeline.md)

## Decisions left open

* The brief does not specify the inference latency target or camera hardware constraints.
* The training compute location and infrastructure for weekly retraining are unspecified.
* The model family, image preprocessing, and inspection-quality metrics are unspecified.
* The process for producing labels and retaining or versioning images is unspecified.
* The device update transport, connectivity recovery, and security controls are unspecified.
* The chosen design point is unattested as a combination in the design space; the checked rival combination was also unattested.
