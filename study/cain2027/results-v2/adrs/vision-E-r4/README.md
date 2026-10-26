# Architecture decisions: On-device visual inspection

* [on device prediction serving](0001-on-device-prediction-serving.md)
* [weekly model training](0002-weekly-model-training.md)
* [model delivery automation](0003-model-delivery-automation.md)
* [production model version strategy](0004-production-model-version-strategy.md)
* [training data versioning](0005-training-data-versioning.md)
* [production model monitoring](0006-production-model-monitoring.md)
* [model release testing](0007-model-release-testing.md)

## Not grounded in the design space

* Device-to-device update transport and retry behavior for intermittently connected cameras.
* Hardware sizing and model format/runtime compatibility across camera devices.
* Image retention, privacy, and security requirements.
* Acceptable prediction latency, quality thresholds, and rollback triggers.
* How labels are collected from production and reconciled with delayed device logs.
