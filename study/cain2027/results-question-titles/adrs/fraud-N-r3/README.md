# Architecture decisions: Card-fraud scoring service

* [Synchronous scoring API](0001-synchronous-scoring-api.md)
* [Replicated stateless scoring instances](0002-replicated-stateless-scoring-instances.md)
* [Versioned model artifacts loaded by scoring service](0003-versioned-model-artifacts-loaded-by-scoring-service.md)
* [Persist per-score audit record](0004-persist-per-score-audit-record.md)

## Decisions left open

* Target latency percentile and numeric service-level objective.
* Peak throughput, traffic shape, and scaling limits.
* Behavior when scoring or required features are unavailable.
* Feature definitions, sources, freshness, and point-in-time reconstruction method.
* Audit record format, retention, access controls, and sensitive-data handling.
* Model training, validation, approval, rollout, and rollback process.
* Required explanation format and whether scores need human-readable reasons.
