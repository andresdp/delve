# Architecture decisions: On-device visual inspection

* [keep inference on the production devices](0001-keep-inference-on-the-production-devices.md)
* [train centrally and distribute versioned model artifacts](0002-train-centrally-and-distribute-versioned-model-artifacts.md)
* [update devices using staged rollback capable releases](0003-update-devices-using-staged-rollback-capable-releases.md)

## Not grounded in the design space

* Required inference latency and throughput per production line.
* Minimum defect-detection accuracy and acceptable false-positive or false-negative rates.
* Device hardware, operating system, and available storage.
* How labelled images are collected, stored, and accessed for training.
* Connectivity pattern and mechanism for delivering updates to offline devices.
* Model evaluation and release acceptance criteria.
