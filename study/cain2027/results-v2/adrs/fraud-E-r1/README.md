# Architecture decisions: Card-fraud scoring service

* [Model as a service](0001-model-as-a-service.md)
* [Microservice based model serving](0002-microservice-based-model-serving.md)
* [Streamed ingestion with real-time processing](0003-streamed-ingestion-with-real-time-processing.md)
* [Feature store](0004-feature-store.md)
* [Model in-production tracking](0005-model-in-production-tracking.md)
* [Rollback to previous model version](0006-rollback-to-previous-model-version.md)
* [Data version repository](0007-data-version-repository.md)

## Decisions left open

* Specific latency and availability targets, peak transaction volume, and failure behavior.
* Feature definitions, storage retention, and secure handling of payment data.
* Model training, validation thresholds, approval controls, and release cadence.
* Audit record schema, retention duration, access controls, and exact score reconstruction method.
