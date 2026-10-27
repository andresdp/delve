# Architecture decisions: Card-fraud scoring service

* [Synchronous request-response scoring](0001-synchronous-request-response-scoring.md)
* [Stateless service with horizontal scaling](0002-stateless-service-with-horizontal-scaling.md)
* [In-process model runtime](0003-in-process-model-runtime.md)
* [Persist a per-score provenance record](0004-persist-a-per-score-provenance-record.md)

## Decisions left open

* Feature definitions, sources, and freshness requirements.
* Model training, validation, approval, and deployment process.
* Score thresholds and authorization policy.
* Provenance record retention period and sensitive-data handling.
* Availability targets, peak volumes, and behavior when scoring or dependencies fail.
