# Architecture decisions: Card-fraud scoring service

* [Use a dedicated model service for transaction scoring](0001-use-a-dedicated-model-service-for-transaction-scoring.md)
* [Serve transaction scores through a real-time model service](0002-serve-transaction-scores-through-a-real-time-model-service.md)
* [Ingest transaction data as a stream](0003-ingest-transaction-data-as-a-stream.md)
* [Process transaction features in real time](0004-process-transaction-features-in-real-time.md)
* [Train fraud models in batches](0005-train-fraud-models-in-batches.md)
* [Keep a previous model version available for rollback](0006-keep-a-previous-model-version-available-for-rollback.md)
* [Track model usage and interpretability in production](0007-track-model-usage-and-interpretability-in-production.md)
* [Performance test the prediction service](0008-performance-test-the-prediction-service.md)

## Decisions left open

* How to guarantee availability and recover from infrastructure or dependency failures during peaks, including redundancy and failover.
* How to define feature computation and storage so that the exact inputs used for each prediction can be reconstructed for auditors.
* How to protect transaction data and audit records, including access control, encryption, and retention.
* How to version model artifacts, feature definitions, and scoring code together.
* How to define fraud model quality thresholds and decide when a model is safe to promote.
