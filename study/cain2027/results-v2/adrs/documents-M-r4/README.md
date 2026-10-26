# Architecture decisions: Large-scale document classification

* [Scheduled batch prediction deployment](0001-scheduled-batch-prediction-deployment.md)
* [Input and feature-drift monitoring](0002-input-and-feature-drift-monitoring.md)
* [Elastic resource scaling](0003-elastic-resource-scaling.md)
* [Containerized inference deployment](0004-containerized-inference-deployment.md)

## Decisions left open

* LLM provider, classifier model, and prompt/version strategy.
* Ground-truth collection and label delay for measuring classification quality.
* Document privacy, retention, and insurer-specific regulatory controls.
* Batch cadence, freshness target, and any per-document latency service level.
