# Architecture decisions: Card-fraud scoring service

* [Use a model service for transaction scoring](0001-use-a-model-service-for-transaction-scoring.md)
* [Serve scores through a real-time microservice](0002-serve-scores-through-a-real-time-microservice.md)
* [Persist features in a feature store](0003-persist-features-in-a-feature-store.md)
* [Track production model inputs and outputs](0004-track-production-model-inputs-and-outputs.md)
* [Version data in a dedicated repository](0005-version-data-in-a-dedicated-repository.md)
* [Process scoring inputs in real time](0006-process-scoring-inputs-in-real-time.md)

## Decisions left open

* Peak-traffic scaling and failover design.
* The specific audit record schema and retention period.
* How to bind each score to an immutable model artifact and exact feature values.
