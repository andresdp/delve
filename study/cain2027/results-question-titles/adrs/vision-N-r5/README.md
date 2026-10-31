# Architecture decisions: On-device visual inspection

* [Run inference on each device](0001-run-inference-on-each-device.md)
* [Devices pull versioned releases when connected](0002-devices-pull-versioned-releases-when-connected.md)
* [Scheduled batch training from a shared image and label store](0003-scheduled-batch-training-from-a-shared-image-and-label-store.md)
* [Stage rollout with a prior-version fallback](0004-stage-rollout-with-a-prior-version-fallback.md)

## Decisions left open

* Target device hardware, operating system, and inference runtime
* Required detection accuracy, latency, and inspection throughput
* How devices receive releases when they have no network access
* Image retention, labeling workflow, and data governance
* Security and authenticity requirements for models and updates
* Acceptance criteria and operational process for detecting model regressions
