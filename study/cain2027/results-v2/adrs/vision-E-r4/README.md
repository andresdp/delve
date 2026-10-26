# Architecture decisions: On-device visual inspection

* [On-device prediction serving](0001-on-device-prediction-serving.md)
* [Weekly model training](0002-weekly-model-training.md)
* [Model delivery automation](0003-model-delivery-automation.md)
* [Production model version strategy](0004-production-model-version-strategy.md)
* [Training data versioning](0005-training-data-versioning.md)
* [Production model monitoring](0006-production-model-monitoring.md)
* [Model release testing](0007-model-release-testing.md)

## Decisions left open

* Device-to-device update transport and retry behavior for intermittently connected cameras.
* Hardware sizing and model format/runtime compatibility across camera devices.
* Image retention, privacy, and security requirements.
* Acceptable prediction latency, quality thresholds, and rollback triggers.
* How labels are collected from production and reconciled with delayed device logs.
