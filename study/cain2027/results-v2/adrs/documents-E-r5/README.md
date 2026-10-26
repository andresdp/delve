# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data partitioning in data pipeline](0003-data-partitioning-in-data-pipeline.md)
* [Model performance monitoring](0004-model-performance-monitoring.md)
* [Data batch based model serving](0005-data-batch-based-model-serving.md)

## Decisions left open

* Business latency target and batch cadence
* Document and prediction storage, retention, and access controls
* How teams discover and retrieve results
* Quality metric, source of ground truth, and drift thresholds
* Whether monitoring should trigger human review, retraining, or model replacement
