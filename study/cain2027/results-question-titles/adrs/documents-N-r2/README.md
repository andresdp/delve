# Architecture decisions: Large-scale document classification

* [Durable queue with asynchronous workers](0001-durable-queue-with-asynchronous-workers.md)
* [Autoscaled inference workers](0002-autoscaled-inference-workers.md)
* [Shared results store with query API](0003-shared-results-store-with-query-api.md)
* [Track labeled evaluation metrics over time](0004-track-labeled-evaluation-metrics-over-time.md)

## Decisions left open

* Document formats, sizes, and privacy or retention constraints
* Required classification latency and availability targets
* Claim type taxonomy and confidence or escalation policy
* Model provider, hosting, versioning, and fallback strategy
* Consumer access patterns, delivery guarantees, and result retention
* Availability and freshness of labeled evaluation data; drift alert thresholds and response process
