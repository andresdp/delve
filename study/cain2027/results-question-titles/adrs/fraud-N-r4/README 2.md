# Architecture decisions: Card-fraud scoring service

* [how should authorization obtain a fraud score](0001-how-should-authorization-obtain-a-fraud-score.md)
* [where should model inference run](0002-where-should-model-inference-run.md)
* [how should features reach inference](0003-how-should-features-reach-inference.md)
* [what should be recorded for audit](0004-what-should-be-recorded-for-audit.md)
* [how should scoring handle traffic peaks](0005-how-should-scoring-handle-traffic-peaks.md)

## Not grounded in the design space

* Required availability target, recovery objectives, and regional deployment model.
* Transaction volume, peak profile, and precise latency percentile and timeout budget.
* Model family, artifact format, runtime, and hardware requirements.
* Feature definitions, data sources, freshness targets, and cache consistency rules.
* Score thresholds, authorization fallback behavior, and human review policy.
* Model release, rollback, monitoring, drift detection, and retraining process.
* Audit retention period, access rules, privacy constraints, and tamper-evidence requirements.
