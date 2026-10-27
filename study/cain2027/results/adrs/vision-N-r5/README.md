# Architecture decisions: On-device visual inspection

* [Run defect detection on the production-line devices](0001-run-defect-detection-on-the-production-line-devices.md)
* [Retrain the model weekly from newly labelled images](0002-retrain-the-model-weekly-from-newly-labelled-images.md)
* [Package and distribute versioned model releases to devices](0003-package-and-distribute-versioned-model-releases-to-devices.md)
* [Validate models before promoting them to production](0004-validate-models-before-promoting-them-to-production.md)

## Decisions left open

* How labelled images are collected, stored, and transferred from offline lines.
* Device hardware, operating system, inference runtime, and model format.
* Model validation metrics and promotion thresholds.
* How devices receive and install packages when disconnected.
* Deployment rollout, rollback, and device health reporting.
* Image retention, access control, and privacy requirements.
