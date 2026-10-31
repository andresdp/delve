# Architecture decisions: Large-scale document classification

* [Queued asynchronous pipeline](0001-queued-asynchronous-pipeline.md)
* [Managed LLM endpoint](0002-managed-llm-endpoint.md)
* [Publish results to a shared event stream](0003-publish-results-to-a-shared-event-stream.md)
* [Monitor labeled outcomes against a quality baseline](0004-monitor-labeled-outcomes-against-a-quality-baseline.md)

## Decisions left open

* Classification taxonomy, confidence thresholds, and handling of ambiguous or unsupported documents.
* Latency and freshness targets for classification and consumer delivery.
* Data sensitivity, retention, residency, and approved LLM provider constraints.
* Label source, volume, and delay for quality measurement.
* Model evaluation, release, rollback, and retraining ownership.
* Availability, recovery, and delivery guarantees expected of the system.
