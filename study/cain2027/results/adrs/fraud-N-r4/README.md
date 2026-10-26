# Architecture decisions: Card-fraud scoring service

* [Synchronous scoring API](0001-synchronous-scoring-api.md)
* [Inference in the scoring service](0002-inference-in-the-scoring-service.md)
* [Use cached online features](0003-use-cached-online-features.md)
* [Persist score and inference snapshot](0004-persist-score-and-inference-snapshot.md)
* [Horizontally scale stateless scoring instances](0005-horizontally-scale-stateless-scoring-instances.md)

## Decisions left open

* Required availability target, recovery objectives, and regional deployment model.
* Transaction volume, peak profile, and precise latency percentile and timeout budget.
* Model family, artifact format, runtime, and hardware requirements.
* Feature definitions, data sources, freshness targets, and cache consistency rules.
* Score thresholds, authorization fallback behavior, and human review policy.
* Model release, rollback, monitoring, drift detection, and retraining process.
* Audit retention period, access rules, privacy constraints, and tamper-evidence requirements.
