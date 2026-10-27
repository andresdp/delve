# Architecture decisions: Large-scale document classification

* [Queue with elastic workers](0001-queue-with-elastic-workers.md)
* [Persist results and publish events](0002-persist-results-and-publish-events.md)
* [Track labeled quality samples over time](0003-track-labeled-quality-samples-over-time.md)

## Decisions left open

* Document formats, ingestion sources, and preprocessing rules.
* Model provider, model selection, and update strategy.
* Classification taxonomy, confidence thresholds, and human review policy.
* Latency and availability targets.
* Data retention, privacy, security, and regulatory requirements.
* Result schema details and consumer delivery guarantees.
* Labeled-data source, sampling rate, and drift alert thresholds.
