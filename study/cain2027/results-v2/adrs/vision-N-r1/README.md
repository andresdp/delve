# Architecture decisions: On-device visual inspection

* [Keep inference on the production devices](0001-keep-inference-on-the-production-devices.md)
* [Train centrally and distribute versioned model artifacts](0002-train-centrally-and-distribute-versioned-model-artifacts.md)
* [Update devices using staged, rollback-capable releases](0003-update-devices-using-staged-rollback-capable-releases.md)

## Decisions left open

* Required inference latency and throughput per production line.
* Minimum defect-detection accuracy and acceptable false-positive or false-negative rates.
* Device hardware, operating system, and available storage.
* How labelled images are collected, stored, and accessed for training.
* Connectivity pattern and mechanism for delivering updates to offline devices.
* Model evaluation and release acceptance criteria.
