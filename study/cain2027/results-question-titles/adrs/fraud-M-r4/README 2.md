# Architecture decisions: Card-fraud scoring service

* [how should transaction scores be served](0001-how-should-transaction-scores-be-served.md)
* [how should serving scale and communicate](0002-how-should-serving-scale-and-communicate.md)
* [how should model versions and scoring inputs be traceable](0003-how-should-model-versions-and-scoring-inputs-be-traceable.md)

## Not grounded in the design space

* The design space does not establish how to capture and retain per-transaction feature values or feature snapshots for audit.
* The brief does not specify scoring failure behavior, such as whether to decline, allow, or route transactions for review when scoring is unavailable.
* The brief does not specify the fraud model family, decision thresholds, or how delayed fraud labels should affect monitoring and retraining.
