# Architecture decisions: On-device visual inspection

* [Run defect inference on-device](0001-run-defect-inference-on-device.md)
* [Automate weekly retraining from new labels](0002-automate-weekly-retraining-from-new-labels.md)
* [Evaluate candidates offline before promotion](0003-evaluate-candidates-offline-before-promotion.md)
* [Version models and lifecycle artifacts](0004-version-models-and-lifecycle-artifacts.md)
* [Automate the recurring ML workflow](0005-automate-the-recurring-ml-workflow.md)

## Decisions left open

* Offline model package transfer to devices when connectivity is unavailable.
* Device fleet rollout, staged deployment, rollback, and recovery from interrupted updates.
* How devices cache labeled images and synchronize them with the training workflow.
* Camera hardware limits, model size, inference latency, and accelerator selection.
* How model evaluation relates to the ML workflow execution coordination choice flagged by the design point.
