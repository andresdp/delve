# Architecture decisions: Large-scale document classification

* [Queued asynchronous ingestion](0001-queued-asynchronous-ingestion.md)
* [Autoscaled stateless workers](0002-autoscaled-stateless-workers.md)
* [Publish results to a shared event stream](0003-publish-results-to-a-shared-event-stream.md)
* [Quality monitoring dashboard with alerts](0004-quality-monitoring-dashboard-with-alerts.md)
* [Versioned, staged model rollout](0005-versioned-staged-model-rollout.md)

## Decisions left open

* Document formats, sizes, and ingestion interfaces
* Claim type taxonomy and labeled quality data
* LLM provider, model, and deployment constraints
* Latency and backlog service objectives
* Data retention, privacy, and security requirements
* Quality metrics, alert thresholds, and operator response process
* Event delivery guarantees and consumer replay needs
