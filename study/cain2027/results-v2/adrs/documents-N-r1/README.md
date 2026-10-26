# Architecture decisions: Large-scale document classification

* [Prioritize the system requirements](0001-prioritize-the-system-requirements.md)
* [Queue-based workers](0002-queue-based-workers.md)
* [Shared result store with read access](0003-shared-result-store-with-read-access.md)
* [Monitor labeled outcomes over time](0004-monitor-labeled-outcomes-over-time.md)

## Decisions left open

* Classification latency target and whether results must be synchronous
* Inference cost or budget limits
* Reproducibility requirements and model or prompt versioning
* Document privacy, retention, and security requirements
* Label source, availability, and drift response process
* Required availability and recovery targets
