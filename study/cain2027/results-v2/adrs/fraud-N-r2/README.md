# Architecture decisions: Card-fraud scoring service

* [Synchronous in-process inference](0001-synchronous-in-process-inference.md)
* [Replicated, horizontally scalable deployment](0002-replicated-horizontally-scalable-deployment.md)
* [Persist model version and feature snapshot with each score](0003-persist-model-version-and-feature-snapshot-with-each-score.md)
* [Pin an explicit model version per serving deployment](0004-pin-an-explicit-model-version-per-serving-deployment.md)

## Decisions left open

* Numerical latency target and percentile
* Peak transaction rate, availability target, and overload behavior
* Feature definitions, sources, freshness, and snapshot encoding
* Audit retention period, access controls, and storage location
* Model training, validation, approval, and rollback process
* Score format, threshold policy, and authorization fallback behavior
