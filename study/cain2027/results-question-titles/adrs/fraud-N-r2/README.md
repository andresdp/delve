# Architecture decisions: Card-fraud scoring service

* [Synchronous scoring API](0001-synchronous-scoring-api.md)
* [Stateless replicated service](0002-stateless-replicated-service.md)
* [Pin a version per scoring deployment](0003-pin-a-version-per-scoring-deployment.md)
* [Persist score, version, and feature snapshot](0004-persist-score-version-and-feature-snapshot.md)

## Decisions left open

* Feature definitions, sources, and computation strategy
* Required audit retention period and access controls
* Timeout, fallback, and authorization behavior when scoring is unavailable
* Deployment platform, peak throughput, and availability targets
* Model training, validation, approval, and rollout process
* Required form of explanation beyond identifying model version and features
