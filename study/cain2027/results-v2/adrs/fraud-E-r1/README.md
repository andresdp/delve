# Architecture decisions: Card-fraud scoring service

* [how to integrate the model](0001-how-to-integrate-the-model.md)
* [how to serve scores](0002-how-to-serve-scores.md)
* [how to ingest and process transaction data](0003-how-to-ingest-and-process-transaction-data.md)
* [how to persist and provide access to features](0004-how-to-persist-and-provide-access-to-features.md)
* [how to track model versions and scoring inputs](0005-how-to-track-model-versions-and-scoring-inputs.md)
* [how to manage model versions in production](0006-how-to-manage-model-versions-in-production.md)
* [how to version data](0007-how-to-version-data.md)

## Not grounded in the design space

* Specific latency and availability targets, peak transaction volume, and failure behavior.
* Feature definitions, storage retention, and secure handling of payment data.
* Model training, validation thresholds, approval controls, and release cadence.
* Audit record schema, retention duration, access controls, and exact score reconstruction method.
