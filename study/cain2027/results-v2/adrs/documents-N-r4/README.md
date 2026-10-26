# Architecture decisions: Large-scale document classification

* [Queue-backed worker pool](0001-queue-backed-worker-pool.md)
* [Shared results store with change events](0002-shared-results-store-with-change-events.md)
* [Metrics with sampled case review](0003-metrics-with-sampled-case-review.md)
* [Version models and record version per result](0004-version-models-and-record-version-per-result.md)

## Decisions left open

* Classification result latency target or freshness SLO.
* Cost limits and compute budget.
* Security, privacy, regulatory, and document retention requirements.
* How ground-truth labels are obtained and who reviews sampled cases.
* Required availability, recovery, and data-loss targets.
* Result schema, consumer delivery guarantees, and event retention.
