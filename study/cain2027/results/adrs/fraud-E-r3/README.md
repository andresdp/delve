# Architecture decisions: Card-fraud scoring service

* [how should the scoring model integrate with the payments app](0001-how-should-the-scoring-model-integrate-with-the-payments-app.md)
* [how should online scores be served](0002-how-should-online-scores-be-served.md)
* [how should features be persisted and accessed](0003-how-should-features-be-persisted-and-accessed.md)
* [how should the system retain evidence for score audits](0004-how-should-the-system-retain-evidence-for-score-audits.md)
* [how should model updates be deployed](0005-how-should-model-updates-be-deployed.md)
* [what production tests should gate model releases](0006-what-production-tests-should-gate-model-releases.md)

## Not grounded in the design space

* Authorization behavior when scoring is unavailable or exceeds the latency budget.
* Exact audit record schema, retention period, and privacy controls.
* Feature computation and retrieval strategy for online scoring.
