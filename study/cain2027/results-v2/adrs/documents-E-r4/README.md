# Architecture decisions: Large-scale document classification

* [main requirements](0001-main-requirements.md)
* [how to serve classification results](0002-how-to-serve-classification-results.md)
* [how to ingest incoming documents](0003-how-to-ingest-incoming-documents.md)
* [batch or real time processing](0004-batch-or-real-time-processing.md)
* [how to parallelize document processing](0005-how-to-parallelize-document-processing.md)
* [how to monitor classification quality](0006-how-to-monitor-classification-quality.md)
* [how to adjust models after monitoring](0007-how-to-adjust-models-after-monitoring.md)

## Not grounded in the design space

* Per-document latency and service availability targets
* LLM provider, model selection, rate limits, and cost controls
* Data retention, privacy, security, and access control
* Quality metric definitions, labels, and drift thresholds
* Batch cadence, retry handling, and failure recovery
* Result schema and inter-team access contract
* Model and prompt versioning and reproducibility
* Human review and escalation for low-confidence predictions
