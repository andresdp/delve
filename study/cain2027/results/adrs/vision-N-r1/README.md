# Architecture decisions: On-device visual inspection

* [Run defect detection on the production-line devices](0001-run-defect-detection-on-the-production-line-devices.md)
* [Retrain the model centrally on newly labelled images](0002-retrain-the-model-centrally-on-newly-labelled-images.md)
* [Distribute versioned model packages to devices](0003-distribute-versioned-model-packages-to-devices.md)
* [Keep inspection operational when model updates are unavailable](0004-keep-inspection-operational-when-model-updates-are-unavailab.md)

## Decisions left open

* Target device hardware and model runtime
* Image retention, transfer, and privacy requirements
* Update authentication, integrity checks, rollout policy, and rollback behavior
* Model acceptance criteria and validation process
* Inspection outputs, alert handling, and failure behavior
* Fleet health monitoring and offline-device reporting
