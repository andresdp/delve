# Architecture decisions: On-device visual inspection

* [On-device edge inference](0001-on-device-edge-inference.md)
* [Progressive release automation with rollback](0002-progressive-release-automation-with-rollback.md)
* [Comprehensive ML lifecycle traceability](0003-comprehensive-ml-lifecycle-traceability.md)
* [Schedule-based retraining trigger](0004-schedule-based-retraining-trigger.md)

## Decisions left open

* How cameras receive model updates while offline, including synchronization and retry behavior.
* How inference behaves during a partially applied update or failed model load.
* Model evaluation and promotion thresholds for defect detection.
* Device identity, access control, and update security.
* Whether drift monitoring should also trigger retraining between weekly runs.
