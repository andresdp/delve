# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should retraining be triggered](0002-how-should-retraining-be-triggered.md)
* [how should candidate models be evaluated](0003-how-should-candidate-models-be-evaluated.md)
* [how should updated models be released](0004-how-should-updated-models-be-released.md)

## Not grounded in the design space

* How devices exchange model packages when network access is unavailable.
* Image and label storage, retention, and transfer to the training environment.
* Training compute and workflow coordination for the weekly cycle.
* Model family and resource fit for the camera hardware.
* Device fleet management, update authentication, and recovery protocol.
