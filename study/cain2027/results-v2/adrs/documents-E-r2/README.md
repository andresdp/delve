# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data batch based model serving](0003-data-batch-based-model-serving.md)
* [Shared data store](0004-shared-data-store.md)
* [Model performance monitoring](0005-model-performance-monitoring.md)
* [Manual model adjustment](0006-manual-model-adjustment.md)

## Decisions left open

* Target classification latency and acceptable result staleness
* How to measure quality drift and obtain labels or ground truth
* LLM provider, model selection, prompt/version management, and reproducibility
* Retry, deduplication, and failure handling for large batch runs
* Data privacy, retention, and access controls across teams
* Capacity, cost, and scaling strategy for seasonal peaks
