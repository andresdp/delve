# Architecture decisions: Card-fraud scoring service

* [Serve scores through a dedicated online inference service](0001-serve-scores-through-a-dedicated-online-inference-service.md)
* [Scale serving capacity for transaction peaks](0002-scale-serving-capacity-for-transaction-peaks.md)
* [Record the model version and features for each score](0003-record-the-model-version-and-features-for-each-score.md)
* [Deploy versioned models with rollback](0004-deploy-versioned-models-with-rollback.md)

## Decisions left open

* Feature sourcing and freshness requirements.
* Model training, validation, and promotion criteria.
* Audit record retention period, storage system, and access policy.
* Timeout, fallback, and authorization behavior when scoring is unavailable.
* Peak volume, service-level target, and capacity limits.
