# Architecture decisions: Large-scale document classification

* [Process classifications asynchronously](0001-process-classifications-asynchronously.md)
* [Scale inference workers with demand](0002-scale-inference-workers-with-demand.md)
* [Expose results through a shared result service](0003-expose-results-through-a-shared-result-service.md)
* [Monitor classification quality drift](0004-monitor-classification-quality-drift.md)

## Decisions left open

* Required classification latency and whether results need ordering.
* Document formats, ingestion channels, and input validation rules.
* Data retention, privacy, security, and regional processing constraints.
* Model provider, model selection, fallback behavior, and update cadence.
* Label source, labeling delay, quality targets, and alert thresholds.
* Result schema, consumer access patterns, and delivery guarantees.
* Availability, recovery, and operational service-level targets.
