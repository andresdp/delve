# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data batch based model serving](0003-data-batch-based-model-serving.md)
* [Data partitioning in data pipeline](0004-data-partitioning-in-data-pipeline.md)
* [Model performance monitoring](0005-model-performance-monitoring.md)

## Decisions left open

* How to establish ground-truth labels and measure classification quality when labels arrive late or are unavailable.
* How to govern claim data, including retention, privacy, access controls, and audit requirements.
* How to version and roll back prompts, models, and classification taxonomies.
* How to handle invalid documents, low-confidence predictions, and human review.
* How to set batch cadence, seasonal capacity targets, latency objectives, and service-level objectives.
* How consuming teams discover and access prediction results and receive availability notifications.
