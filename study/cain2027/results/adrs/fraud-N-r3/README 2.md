# Architecture decisions: Card-fraud scoring service

* [how should transactions receive fraud scores](0001-how-should-transactions-receive-fraud-scores.md)
* [how should scoring stay available during peaks](0002-how-should-scoring-stay-available-during-peaks.md)
* [how should model versions be served](0003-how-should-model-versions-be-served.md)
* [how should score inputs and model identity be auditable](0004-how-should-score-inputs-and-model-identity-be-auditable.md)

## Not grounded in the design space

* Target latency percentile and numeric service-level objective.
* Peak throughput, traffic shape, and scaling limits.
* Behavior when scoring or required features are unavailable.
* Feature definitions, sources, freshness, and point-in-time reconstruction method.
* Audit record format, retention, access controls, and sensitive-data handling.
* Model training, validation, approval, rollout, and rollback process.
* Required explanation format and whether scores need human-readable reasons.
