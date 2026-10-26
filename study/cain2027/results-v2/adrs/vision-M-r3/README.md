# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Online computation serving](0002-online-computation-serving.md)
* [Schedule-based retraining trigger](0003-schedule-based-retraining-trigger.md)
* [Progressive release automation with rollback](0004-progressive-release-automation-with-rollback.md)
* [Comprehensive ML lifecycle traceability](0005-comprehensive-ml-lifecycle-traceability.md)

## Decisions left open

* Device fleet management and update transport for cameras with intermittent connectivity.
* Image storage, retention, and transfer for newly labelled training data.
* The model's accuracy target and the validation gate before promotion.
* Device hardware, model size, and runtime compatibility constraints.
* The recovery behavior when a device update is interrupted.
