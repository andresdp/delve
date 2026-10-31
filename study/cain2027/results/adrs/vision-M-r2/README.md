# Architecture decisions: On-device visual inspection

* [Run visual inspection inference on-device at the production line](0001-run-visual-inspection-inference-on-device-at-the-production-.md)
* [Retrain on a weekly schedule](0002-retrain-on-a-weekly-schedule.md)
* [Automate recurring ML lifecycle workflows](0003-automate-recurring-ml-lifecycle-workflows.md)

## Decisions left open

* Device update transport and offline synchronization behavior.
* How updates are staged, validated, and rolled back across production devices.
* Image labeling workflow and dataset storage.
* Model evaluation thresholds and promotion criteria.
* Device hardware limits, model format, and inference performance targets.
* Monitoring and health reporting when devices are offline.
