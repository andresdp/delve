# Architecture decisions: Large-scale document classification

* [Model in batch prediction system](0001-model-in-batch-prediction-system.md)
* [Hybrid online/offline model serving](0002-hybrid-online-offline-model-serving.md)
* [Data ingestion in batches](0003-data-ingestion-in-batches.md)
* [Data partitioning in data pipeline](0004-data-partitioning-in-data-pipeline.md)
* [Shared data store](0005-shared-data-store.md)
* [Push notification](0006-push-notification.md)
* [Model performance monitoring](0007-model-performance-monitoring.md)

## Decisions left open

* Document privacy, security, and regulatory controls.
* Storage technology, retention, and deletion rules.
* Model evaluation method, quality thresholds, and drift detection approach.
* LLM provider, model choice, prompt management, and fallback behavior.
* Batch schedule, latency targets, retry policy, and failure recovery.
* Consumer result schema, access control, and notification protocol.
* Seasonal capacity targets, scaling policy, and cost limits.
