# Architecture decisions: Card-fraud scoring service

* [model integration](0001-model-integration.md)
* [prediction serving](0002-prediction-serving.md)
* [feature persistence and access](0003-feature-persistence-and-access.md)
* [model version rollout](0004-model-version-rollout.md)
* [production tracking](0005-production-tracking.md)
* [prediction service validation](0006-prediction-service-validation.md)

## Not grounded in the design space

* Exact latency objective and peak transaction rate.
* Feature definitions, freshness, storage layout, and retention policy.
* Audit record schema, retention period, access controls, and privacy requirements.
* Model training, validation, approval, and release criteria.
* Availability targets, failover behavior, and authorization behavior when scoring is unavailable.
* Runtime, deployment platform, and service communication protocol.
