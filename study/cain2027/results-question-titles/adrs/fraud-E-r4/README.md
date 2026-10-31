# Architecture decisions: Card-fraud scoring service

* [Model integration](0001-model-integration.md)
* [Prediction serving](0002-prediction-serving.md)
* [Feature persistence and access](0003-feature-persistence-and-access.md)
* [Model version rollout](0004-model-version-rollout.md)
* [Production tracking](0005-production-tracking.md)
* [Prediction service validation](0006-prediction-service-validation.md)

## Decisions left open

* Exact latency objective and peak transaction rate.
* Feature definitions, freshness, storage layout, and retention policy.
* Audit record schema, retention period, access controls, and privacy requirements.
* Model training, validation, approval, and release criteria.
* Availability targets, failover behavior, and authorization behavior when scoring is unavailable.
* Runtime, deployment platform, and service communication protocol.
