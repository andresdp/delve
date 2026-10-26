# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should labeled images be produced](0002-how-should-labeled-images-be-produced.md)
* [how should weekly model candidates be trained and tuned](0003-how-should-weekly-model-candidates-be-trained-and-tuned.md)
* [how should model releases reach devices](0004-how-should-model-releases-reach-devices.md)
* [how should models and training runs be tracked](0005-how-should-models-and-training-runs-be-tracked.md)
* [how should deployed models be monitored and adapted](0006-how-should-deployed-models-be-monitored-and-adapted.md)

## Not grounded in the design space

* Model evaluation metrics and acceptance thresholds for defect detection.
* Device update protocol, security, and behavior when a device remains offline for an extended period.
* Target hardware limits, model format, and runtime compatibility.
* Data retention, privacy, and access controls for production images.
* Rollback triggers and responsibility for release approval.
