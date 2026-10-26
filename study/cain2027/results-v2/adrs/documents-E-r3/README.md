# Architecture decisions: Large-scale document classification

* [Hybrid online/offline model serving](0001-hybrid-online-offline-model-serving.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data partitioning in data pipeline](0003-data-partitioning-in-data-pipeline.md)
* [Model performance monitoring](0004-model-performance-monitoring.md)

## Decisions left open

* How to obtain timely ground truth or other feedback for measuring classification quality.
* Latency and freshness targets for results consumed by teams.
* Document retention, privacy, and access controls for an insurer's data.
* LLM selection, prompt or model version management, and fallback behavior.
* Team-facing result schema, delivery contract, and failure handling.
* Seasonal capacity limits and cost targets.
