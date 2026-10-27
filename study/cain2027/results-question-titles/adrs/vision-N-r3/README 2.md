# Architecture decisions: On-device visual inspection

* [where should defect inference run](0001-where-should-defect-inference-run.md)
* [how should devices receive model updates](0002-how-should-devices-receive-model-updates.md)
* [how should models be validated before release](0003-how-should-models-be-validated-before-release.md)
* [how should model installation handle failures](0004-how-should-model-installation-handle-failures.md)

## Not grounded in the design space

* How labelled images are collected, stored, and transferred from production lines.
* Required inference latency, throughput, and device hardware constraints.
* Model quality metrics, release thresholds, and validation-set ownership.
* Device fleet size, connectivity patterns, and update scheduling requirements.
* Security, access control, and signing requirements for images and model artifacts.
* How inference results, failures, and device health are monitored and retained.
