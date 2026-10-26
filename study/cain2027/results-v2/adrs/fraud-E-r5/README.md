# Architecture decisions: Card-fraud scoring service

* [Model integration](0001-model-integration.md)
* [Online score serving](0002-online-score-serving.md)
* [Feature persistence and access](0003-feature-persistence-and-access.md)
* [Model version deployment](0004-model-version-deployment.md)
* [Production model tracking](0005-production-model-tracking.md)

## Decisions left open

* The brief does not specify a numeric latency budget, peak throughput, or availability target.
* The design space does not determine a durable audit event schema, retention period, or tamper controls for linking each score to its exact model version and feature values.
* The design space does not cover payment authorization behavior when scoring is unavailable, including timeout and fallback policy.
