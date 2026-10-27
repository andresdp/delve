# Architecture decisions: On-device visual inspection

* [Use batch ETL for weekly labelled-image ingestion](0001-use-batch-etl-for-weekly-labelled-image-ingestion.md)
* [Use an orchestrated pipeline for weekly training and evaluation](0002-use-an-orchestrated-pipeline-for-weekly-training-and-evaluat.md)
* [Run inference on each production line device](0003-run-inference-on-each-production-line-device.md)
* [Use progressive releases with rollback for model updates](0004-use-progressive-releases-with-rollback-for-model-updates.md)
* [Gate model promotion on offline evaluation](0005-gate-model-promotion-on-offline-evaluation.md)
* [Monitor device health and input data quality](0006-monitor-device-health-and-input-data-quality.md)
* [Use vertically scalable training initially](0007-use-vertically-scalable-training-initially.md)

## Decisions left open

* How to deliver and reconcile model updates on devices that are offline during a release.
* Device hardware, runtime, and local storage sizing.
* Image retention, privacy, and access controls.
* Defect quality metrics and acceptable promotion thresholds; the brief does not specify them.
* Operational response when a device cannot report monitoring data.
