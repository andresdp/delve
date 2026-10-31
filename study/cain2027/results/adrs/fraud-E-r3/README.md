# Architecture decisions: Card-fraud scoring service

* [Serve fraud scores through a dedicated online model service](0001-serve-fraud-scores-through-a-dedicated-online-model-service.md)
* [Use microservice based online model serving](0002-use-microservice-based-online-model-serving.md)
* [Persist and provide features through a feature store](0003-persist-and-provide-features-through-a-feature-store.md)
* [Deploy multiple model versions in production](0004-deploy-multiple-model-versions-in-production.md)
* [Track model usage, inputs, outputs, and interpretability in production](0005-track-model-usage-inputs-outputs-and-interpretability-in-pro.md)
* [Performance test the prediction service](0006-performance-test-the-prediction-service.md)

## Decisions left open

* The exact audit event schema and immutable linkage among transaction, model version, feature values, score, and explanation.
* Feature-store online lookup design, consistency guarantees, and retention.
* The explainability method and the explanation format returned to auditors.
* Availability targets, failover topology, timeout behavior, and authorization fallback when scoring is unavailable.
* Model rollout, traffic routing, rollback procedure, and version retirement policy.
* Security, access control, encryption, and retention requirements for sensitive transaction and audit data.
