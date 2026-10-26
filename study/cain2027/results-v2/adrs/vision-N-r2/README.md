# Architecture decisions: On-device visual inspection

* [Run inference on each device](0001-run-inference-on-each-device.md)
* [Managed cloud training](0002-managed-cloud-training.md)
* [Downloadable signed model packages](0003-downloadable-signed-model-packages.md)
* [Validate, stage, and retain a rollback version](0004-validate-stage-and-retain-a-rollback-version.md)

## Decisions left open

* Inference latency and accuracy targets
* Device hardware, operating system, and fleet size
* Image capture, labelling, storage, retention, and transfer process
* Training data access controls and privacy requirements
* Model evaluation criteria and required validation data
* Device connectivity patterns and update scheduling
* Model package integrity, device authentication, and key management
* Monitoring, defect-result retention, and operational alerting
* Budget limits and acceptable cloud service dependencies
