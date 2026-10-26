# Architecture decisions: On-device visual inspection

* [On-device inference](0001-on-device-inference.md)
* [Direct device download from a central model store](0002-direct-device-download-from-a-central-model-store.md)
* [Automated evaluation against a fixed validation set](0003-automated-evaluation-against-a-fixed-validation-set.md)
* [Stage, verify, then activate with rollback](0004-stage-verify-then-activate-with-rollback.md)

## Decisions left open

* How labelled images are collected, stored, and transferred from production lines.
* Required inference latency, throughput, and device hardware constraints.
* Model quality metrics, release thresholds, and validation-set ownership.
* Device fleet size, connectivity patterns, and update scheduling requirements.
* Security, access control, and signing requirements for images and model artifacts.
* How inference results, failures, and device health are monitored and retained.
