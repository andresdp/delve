# Architecture decisions: On-device visual inspection

* [where should inspection inference run](0001-where-should-inspection-inference-run.md)
* [how should weekly training candidates be evaluated](0002-how-should-weekly-training-candidates-be-evaluated.md)
* [how are training images labeled](0003-how-are-training-images-labeled.md)
* [what triggers retraining](0004-what-triggers-retraining.md)
* [how should model and training artifacts be tracked](0005-how-should-model-and-training-artifacts-be-tracked.md)
* [how should model updates reach production devices](0006-how-should-model-updates-reach-production-devices.md)
* [what should production monitoring cover](0007-what-should-production-monitoring-cover.md)

## Not grounded in the design space

* How offline devices receive, authenticate, and resume model updates.
* Model family, image preprocessing, and device-specific resource limits.
* Label review ownership, image retention, and data access policy.
* Workflow execution coordination required by evaluation; the design space point warned this prerequisite was undecided.
* Monitoring telemetry transport, alerting, and behavior during network outages.
