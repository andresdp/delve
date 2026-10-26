# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should retraining start](0002-how-should-retraining-start.md)
* [how should candidates be checked before release](0003-how-should-candidates-be-checked-before-release.md)
* [how should model updates reach devices](0004-how-should-model-updates-reach-devices.md)
* [how should retraining and evaluation steps be coordinated](0005-how-should-retraining-and-evaluation-steps-be-coordinated.md)

## Not grounded in the design space

* The brief does not specify the inference latency target or camera hardware constraints.
* The training compute location and infrastructure for weekly retraining are unspecified.
* The model family, image preprocessing, and inspection-quality metrics are unspecified.
* The process for producing labels and retaining or versioning images is unspecified.
* The device update transport, connectivity recovery, and security controls are unspecified.
* The chosen design point is unattested as a combination in the design space; the checked rival combination was also unattested.
