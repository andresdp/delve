# Architecture decisions: Card-fraud scoring service

* [model integration](0001-model-integration.md)
* [online score serving](0002-online-score-serving.md)
* [feature persistence and access](0003-feature-persistence-and-access.md)
* [model version deployment](0004-model-version-deployment.md)
* [production model tracking](0005-production-model-tracking.md)

## Not grounded in the design space

* The brief does not specify a numeric latency budget, peak throughput, or availability target.
* The design space does not determine a durable audit event schema, retention period, or tamper controls for linking each score to its exact model version and feature values.
* The design space does not cover payment authorization behavior when scoring is unavailable, including timeout and fallback policy.
