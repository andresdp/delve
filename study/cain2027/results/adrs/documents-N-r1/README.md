# Architecture decisions: Large-scale document classification

* [Use a durable queue to buffer classification work](0001-use-a-durable-queue-to-buffer-classification-work.md)
* [Scale stateless classification workers horizontally](0002-scale-stateless-classification-workers-horizontally.md)
* [Publish classification results as events](0003-publish-classification-results-as-events.md)
* [Version the classifier and record each prediction's version](0004-version-the-classifier-and-record-each-prediction-s-version.md)
* [Monitor quality using labeled outcomes and drift indicators](0005-monitor-quality-using-labeled-outcomes-and-drift-indicators.md)

## Decisions left open

* Document formats, sizes, and ingestion interfaces
* Required classification latency and backlog objectives
* Claim-type taxonomy, confidence thresholds, and human-review policy
* Data residency, retention, and privacy requirements
* LLM provider, deployment model, rate limits, and cost targets
* Availability, recovery, and delivery guarantees for consumers
* Source and timing of ground-truth labels
