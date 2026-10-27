# Architecture decisions: Card-fraud scoring service

* [how should transactions be scored](0001-how-should-transactions-be-scored.md)
* [how should the scoring service handle peaks](0002-how-should-the-scoring-service-handle-peaks.md)
* [where should model inference run](0003-where-should-model-inference-run.md)
* [how should score provenance be captured](0004-how-should-score-provenance-be-captured.md)

## Not grounded in the design space

* Feature definitions, sources, and freshness requirements.
* Model training, validation, approval, and deployment process.
* Score thresholds and authorization policy.
* Provenance record retention period and sensitive-data handling.
* Availability targets, peak volumes, and behavior when scoring or dependencies fail.
