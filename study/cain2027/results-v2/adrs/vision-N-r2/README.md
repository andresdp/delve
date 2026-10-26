# Architecture decisions: On-device visual inspection

* [where should inference run](0001-where-should-inference-run.md)
* [how should models be retrained](0002-how-should-models-be-retrained.md)
* [how should model updates reach devices](0003-how-should-model-updates-reach-devices.md)
* [how should model releases be promoted](0004-how-should-model-releases-be-promoted.md)

## Not grounded in the design space

* Inference latency and accuracy targets
* Device hardware, operating system, and fleet size
* Image capture, labelling, storage, retention, and transfer process
* Training data access controls and privacy requirements
* Model evaluation criteria and required validation data
* Device connectivity patterns and update scheduling
* Model package integrity, device authentication, and key management
* Monitoring, defect-result retention, and operational alerting
* Budget limits and acceptable cloud service dependencies
