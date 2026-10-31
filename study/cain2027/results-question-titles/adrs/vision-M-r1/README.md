# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Human-in-the-loop data labeling](0002-human-in-the-loop-data-labeling.md)
* [Automated hyperparameter optimization](0003-automated-hyperparameter-optimization.md)
* [Commit-triggered staged release automation](0004-commit-triggered-staged-release-automation.md)
* [End-to-end reproducible lifecycle governance](0005-end-to-end-reproducible-lifecycle-governance.md)
* [Periodic model health checks](0006-periodic-model-health-checks.md)

## Decisions left open

* Model evaluation metrics and acceptance thresholds for defect detection.
* Device update protocol, security, and behavior when a device remains offline for an extended period.
* Target hardware limits, model format, and runtime compatibility.
* Data retention, privacy, and access controls for production images.
* Rollback triggers and responsibility for release approval.
