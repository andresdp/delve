# Architecture decisions: Card-fraud scoring service

* [Use a model service for transaction scoring](0001-use-a-model-service-for-transaction-scoring.md)
* [Serve fraud scores through a real-time microservice](0002-serve-fraud-scores-through-a-real-time-microservice.md)
* [Use a feature store for scoring features](0003-use-a-feature-store-for-scoring-features.md)
* [Track model usage, inputs, and outputs in production](0004-track-model-usage-inputs-and-outputs-in-production.md)
* [Keep multiple model versions in production](0005-keep-multiple-model-versions-in-production.md)
* [Process transaction inputs in real time](0006-process-transaction-inputs-in-real-time.md)

## Decisions left open

* Exact audit record schema and retention period for model version, feature values, and score.
* Feature store consistency and lookup latency guarantees.
* Peak throughput, capacity strategy, and behavior when scoring is unavailable.
* Model rollout, traffic allocation, and rollback policy.
* Transaction data privacy, access controls, and audit access procedures.
* Training data ingestion, model evaluation thresholds, and retraining cadence.
