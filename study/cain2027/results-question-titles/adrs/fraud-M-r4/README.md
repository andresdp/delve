# Architecture decisions: Card-fraud scoring service

* [Queue-fronted online serving cluster](0001-queue-fronted-online-serving-cluster.md)
* [Stateless horizontally scaled serving](0002-stateless-horizontally-scaled-serving.md)
* [Comprehensive ML lifecycle traceability](0003-comprehensive-ml-lifecycle-traceability.md)

## Decisions left open

* The design space does not establish how to capture and retain per-transaction feature values or feature snapshots for audit.
* The brief does not specify scoring failure behavior, such as whether to decline, allow, or route transactions for review when scoring is unavailable.
* The brief does not specify the fraud model family, decision thresholds, or how delayed fraud labels should affect monitoring and retraining.
