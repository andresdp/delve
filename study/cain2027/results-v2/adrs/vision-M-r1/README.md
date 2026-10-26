# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should weekly training and validation run](0002-how-should-weekly-training-and-validation-run.md)
* [how should retraining be triggered](0003-how-should-retraining-be-triggered.md)
* [how should candidate models be evaluated](0004-how-should-candidate-models-be-evaluated.md)
* [how should model releases be controlled](0005-how-should-model-releases-be-controlled.md)
* [how much lifecycle state should be versioned](0006-how-much-lifecycle-state-should-be-versioned.md)
* [what should production monitoring cover](0007-what-should-production-monitoring-cover.md)

## Not grounded in the design space

* Device-to-device update transport and integrity when cameras are offline.
* Model format, hardware compatibility, and device rollback mechanics.
* Image retention, privacy, and newly labelled data transfer from production lines.
* Latency, memory, and throughput targets for inference on camera hardware.
* The specific defect-quality metric and acceptance thresholds for promotion.
