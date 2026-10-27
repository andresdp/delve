# Architecture decisions: On-device visual inspection

* [Run defect inference on the production-line devices](0001-run-defect-inference-on-the-production-line-devices.md)
* [Train models weekly from newly labelled images](0002-train-models-weekly-from-newly-labelled-images.md)
* [Push versioned model packages to devices](0003-push-versioned-model-packages-to-devices.md)
* [Keep inference independent of network services](0004-keep-inference-independent-of-network-services.md)

## Decisions left open

* Device hardware, operating system, and accelerator capabilities
* Required inference latency, throughput, and defect-detection quality
* Image retention, labelling workflow, and dataset governance
* Model evaluation and release acceptance criteria
* Update transport, device authentication, and recovery behavior
* Fleet monitoring and offline diagnostics
