# Architecture decisions: Large-scale document classification

* [Queue-fronted online serving cluster](0001-queue-fronted-online-serving-cluster.md)
* [Elastic resource scaling](0002-elastic-resource-scaling.md)
* [Input and feature-drift monitoring + real-time prediction-quality monitoring](0003-input-and-feature-drift-monitoring-real-time-prediction-qual.md)

## Decisions left open

* The LLM model, provider, and inference-cost strategy.
* Document ingestion, retries, deduplication, and ordering guarantees.
* The result contract, persistence, and access controls for consuming teams.
* Label collection and evaluation policy for delayed quality measurement.
* Data privacy, retention, and security requirements.
