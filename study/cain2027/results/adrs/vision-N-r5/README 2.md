# Architecture decisions: On-device visual inspection

* [where should defect inference run](0001-where-should-defect-inference-run.md)
* [how should weekly models reach devices](0002-how-should-weekly-models-reach-devices.md)
* [how should training consume newly labeled images](0003-how-should-training-consume-newly-labeled-images.md)
* [how should model releases be checked and reversed](0004-how-should-model-releases-be-checked-and-reversed.md)

## Not grounded in the design space

* Target device hardware, operating system, and inference runtime
* Required detection accuracy, latency, and inspection throughput
* How devices receive releases when they have no network access
* Image retention, labeling workflow, and data governance
* Security and authenticity requirements for models and updates
* Acceptance criteria and operational process for detecting model regressions
