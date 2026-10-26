# Architecture decisions: Large-scale document classification

* [process classifications asynchronously](0001-process-classifications-asynchronously.md)
* [scale inference workers with demand](0002-scale-inference-workers-with-demand.md)
* [expose results through a shared result service](0003-expose-results-through-a-shared-result-service.md)
* [monitor classification quality drift](0004-monitor-classification-quality-drift.md)

## Not grounded in the design space

* Required classification latency and whether results need ordering.
* Document formats, ingestion channels, and input validation rules.
* Data retention, privacy, security, and regional processing constraints.
* Model provider, model selection, fallback behavior, and update cadence.
* Label source, labeling delay, quality targets, and alert thresholds.
* Result schema, consumer access patterns, and delivery guarantees.
* Availability, recovery, and operational service-level targets.
