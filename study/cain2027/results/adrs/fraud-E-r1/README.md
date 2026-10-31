# Architecture decisions: Card-fraud scoring service

* [Use a model service for transaction scoring](0001-use-a-model-service-for-transaction-scoring.md)
* [Serve scores through a real-time microservice](0002-serve-scores-through-a-real-time-microservice.md)
* [Ingest and process transaction data as streams](0003-ingest-and-process-transaction-data-as-streams.md)
* [Persist and provide features through a feature store](0004-persist-and-provide-features-through-a-feature-store.md)
* [Track model use, inputs, and outputs in production](0005-track-model-use-inputs-and-outputs-in-production.md)
* [Test prediction service performance before deployment](0006-test-prediction-service-performance-before-deployment.md)

## Decisions left open

* Fraud-model choice, training data, and retraining cadence.
* Specific latency budget, peak throughput, scaling, and availability targets.
* Audit record schema, retention period, access controls, and tamper resistance.
* Feature definitions, point-in-time consistency, and score reproducibility requirements.
* Model release approval and rollout policy. The design space includes version deployment choices (d:10), but the selected point was not checked with that decision.
