# Architecture decisions: Card-fraud scoring service

* [how should transaction scores be served](0001-how-should-transaction-scores-be-served.md)
* [how should peak load be handled](0002-how-should-peak-load-be-handled.md)
* [what score evidence should be retained](0003-what-score-evidence-should-be-retained.md)
* [how should model versions be selected for scoring](0004-how-should-model-versions-be-selected-for-scoring.md)

## Not grounded in the design space

* Numerical latency target and percentile
* Peak transaction rate, availability target, and overload behavior
* Feature definitions, sources, freshness, and snapshot encoding
* Audit retention period, access controls, and storage location
* Model training, validation, approval, and rollback process
* Score format, threshold policy, and authorization fallback behavior
