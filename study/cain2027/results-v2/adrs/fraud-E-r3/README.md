# Architecture decisions: Card-fraud scoring service

* [how should transaction scores be served](0001-how-should-transaction-scores-be-served.md)
* [how should online features be provided](0002-how-should-online-features-be-provided.md)
* [how should data be versioned for reproducibility](0003-how-should-data-be-versioned-for-reproducibility.md)
* [how should deployed model versions be managed](0004-how-should-deployed-model-versions-be-managed.md)
* [how should production scoring be tracked](0005-how-should-production-scoring-be-tracked.md)

## Not grounded in the design space

* Peak-load capacity targets, scaling policy, and overload behavior.
* Score latency budget allocation, timeout behavior, and authorization fallback.
* Feature snapshot format, audit retention period, and sensitive-data controls.
* Model quality acceptance criteria and release approval process.
