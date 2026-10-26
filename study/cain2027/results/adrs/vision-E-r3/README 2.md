# Architecture decisions: On-device visual inspection

* [how to train the model](0001-how-to-train-the-model.md)
* [how to structure model building](0002-how-to-structure-model-building.md)
* [how to version training data](0003-how-to-version-training-data.md)
* [how to serve predictions on devices](0004-how-to-serve-predictions-on-devices.md)
* [how to deploy model updates and recover from regressions](0005-how-to-deploy-model-updates-and-recover-from-regressions.md)
* [how to automate integration and delivery](0006-how-to-automate-integration-and-delivery.md)
* [what to validate before releasing a model](0007-what-to-validate-before-releasing-a-model.md)
* [how to monitor models in production](0008-how-to-monitor-models-in-production.md)

## Not grounded in the design space

* How to package, authenticate, and securely deliver model updates to devices.
* How devices stage updates, verify them, and resume safely after interrupted connectivity.
* How to measure defect-detection quality and set release thresholds.
* How to handle camera calibration, image drift, and production-line changes.
* Device hardware, runtime, storage, and compute constraints.
