# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Offline evaluation pipeline](0002-offline-evaluation-pipeline.md)
* [Human-in-the-loop data labeling](0003-human-in-the-loop-data-labeling.md)
* [Schedule-based retraining trigger](0004-schedule-based-retraining-trigger.md)
* [Comprehensive ML lifecycle traceability](0005-comprehensive-ml-lifecycle-traceability.md)
* [Progressive release automation with rollback](0006-progressive-release-automation-with-rollback.md)
* [Input and feature-drift monitoring](0007-input-and-feature-drift-monitoring.md)

## Decisions left open

* How offline devices receive, authenticate, and resume model updates.
* Model family, image preprocessing, and device-specific resource limits.
* Label review ownership, image retention, and data access policy.
* Workflow execution coordination required by evaluation; the design space point warned this prerequisite was undecided.
* Monitoring telemetry transport, alerting, and behavior during network outages.
