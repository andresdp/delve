# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should predictions be produced](0002-how-should-predictions-be-produced.md)
* [how should weekly retraining start](0003-how-should-weekly-retraining-start.md)
* [how should model releases reach devices](0004-how-should-model-releases-reach-devices.md)
* [what model lifecycle information should be versioned](0005-what-model-lifecycle-information-should-be-versioned.md)

## Not grounded in the design space

* Device fleet management and update transport for cameras with intermittent connectivity.
* Image storage, retention, and transfer for newly labelled training data.
* The model's accuracy target and the validation gate before promotion.
* Device hardware, model size, and runtime compatibility constraints.
* The recovery behavior when a device update is interrupted.
