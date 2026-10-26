# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should retraining be triggered and run](0002-how-should-retraining-be-triggered-and-run.md)
* [how should model updates be released](0003-how-should-model-updates-be-released.md)
* [how much model lifecycle metadata should be governed](0004-how-much-model-lifecycle-metadata-should-be-governed.md)

## Not grounded in the design space

* Device enrollment, update transport, and offline synchronization policy.
* Camera hardware constraints and model compatibility requirements.
* Image retention, labeling workflow, and dataset access controls.
* Model acceptance thresholds and validation criteria before release.
* Production monitoring and alerting for device health, data quality, and inspection accuracy.
