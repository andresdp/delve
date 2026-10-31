# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data partitioning in data pipeline](0003-data-partitioning-in-data-pipeline.md)
* [Data batch based model serving](0004-data-batch-based-model-serving.md)
* [Shared data store](0005-shared-data-store.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)

## Decisions left open

* How to define classification quality metrics and drift thresholds.
* How to manage document privacy, retention, and access controls.
* How to select, prompt, evaluate, and update the LLM classifier.
* How consumers discover results and handle failed or delayed batches.
* How to provision elastic capacity and meet latency or availability targets.
