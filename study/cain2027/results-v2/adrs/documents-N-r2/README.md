# Architecture decisions: Large-scale document classification

* [Process classifications asynchronously](0001-process-classifications-asynchronously.md)
* [Scale inference workers with demand](0002-scale-inference-workers-with-demand.md)
* [Track quality by model and time](0003-track-quality-by-model-and-time.md)
* [Publish results through a shared result store](0004-publish-results-through-a-shared-result-store.md)

## Decisions left open

* Required classification latency and availability targets.
* Document formats, sizes, and ingestion interface.
* Label source, delay, and quality metric for drift detection.
* Model selection, hosting constraints, and fallback or human-review policy.
* Result retention, privacy, and access requirements.
