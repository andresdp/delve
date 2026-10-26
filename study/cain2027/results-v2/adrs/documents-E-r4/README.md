# Architecture decisions: Large-scale document classification

* [Main requirements](0001-main-requirements.md)
* [Data batch based model serving](0002-data-batch-based-model-serving.md)
* [Data ingestion in batches](0003-data-ingestion-in-batches.md)
* [Batch or real-time processing](0004-batch-or-real-time-processing.md)
* [Data partitioning in data pipeline](0005-data-partitioning-in-data-pipeline.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)
* [Manual model adjustment](0007-manual-model-adjustment.md)

## Decisions left open

* Per-document latency and service availability targets
* LLM provider, model selection, rate limits, and cost controls
* Data retention, privacy, security, and access control
* Quality metric definitions, labels, and drift thresholds
* Batch cadence, retry handling, and failure recovery
* Result schema and inter-team access contract
* Model and prompt versioning and reproducibility
* Human review and escalation for low-confidence predictions
