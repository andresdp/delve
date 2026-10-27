# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data batch based model serving](0003-data-batch-based-model-serving.md)
* [Model performance monitoring](0004-model-performance-monitoring.md)

## Decisions left open

* Autoscaling and capacity planning for seasonal volume.
* Access control and result contracts for consuming teams.
* How to obtain quality labels and set drift thresholds.
* Model update, review, and rollback policy.
