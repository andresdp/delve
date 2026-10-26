# Architecture decisions: On-device visual inspection

* [how should predictions be served on production devices](0001-how-should-predictions-be-served-on-production-devices.md)
* [how should the model integrate with the camera application](0002-how-should-the-model-integrate-with-the-camera-application.md)
* [how should weekly retraining be triggered](0003-how-should-weekly-retraining-be-triggered.md)
* [how should the model be trained](0004-how-should-the-model-be-trained.md)
* [how should training data be versioned](0005-how-should-training-data-be-versioned.md)
* [how should models be delivered to devices](0006-how-should-models-be-delivered-to-devices.md)
* [what should be tested before model release](0007-what-should-be-tested-before-model-release.md)
* [how should model versions be deployed and recovered](0008-how-should-model-versions-be-deployed-and-recovered.md)

## Not grounded in the design space

* Device update transport, synchronization, and recovery when devices reconnect.
* Model and dataset artifact storage and distribution topology.
* Device hardware capacity, model size, and inference latency targets.
* Security and integrity checks for model artifacts.
* Monitoring and reporting from intermittently connected devices.
