# Architecture decisions: Card-fraud scoring service

* [Model as a service](0001-model-as-a-service.md)
* [Microservice based model serving](0002-microservice-based-model-serving.md)
* [Feature store](0003-feature-store.md)
* [Model in-production tracking](0004-model-in-production-tracking.md)
* [Rollback to previous model version](0005-rollback-to-previous-model-version.md)
* [Canary testing](0006-canary-testing.md)

## Decisions left open

* Authorization behavior when scoring is unavailable or exceeds the latency budget.
* Exact audit record schema, retention period, and privacy controls.
* Feature computation and retrieval strategy for online scoring.
