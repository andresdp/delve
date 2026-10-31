# Architecture decisions: Card-fraud scoring service

* [Compute fraud scores online for each transaction](0001-compute-fraud-scores-online-for-each-transaction.md)
* [Expose scoring through a REST prediction microservice](0002-expose-scoring-through-a-rest-prediction-microservice.md)
* [Scale scoring resources elastically for transaction peaks](0003-scale-scoring-resources-elastically-for-transaction-peaks.md)
* [Serve online features from a low-latency feature pipeline](0004-serve-online-features-from-a-low-latency-feature-pipeline.md)
* [Track model and data lineage across the ML lifecycle](0005-track-model-and-data-lineage-across-the-ml-lifecycle.md)
* [Monitor service health and feature drift in production](0006-monitor-service-health-and-feature-drift-in-production.md)

## Decisions left open

* Per-transaction immutable audit record format and retention for the exact model version, feature values, score, and timestamp.
* Authorization behavior when the scoring service or online feature store is unavailable.
* Fraud-specific score threshold and downstream approve, decline, or review policy.
