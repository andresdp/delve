# Architecture decisions: Card-fraud scoring service

* [Use synchronous model serving for pre-authorization fraud scores](0001-use-synchronous-model-serving-for-pre-authorization-fraud-sc.md)
* [Serve low-latency features from an online feature store](0002-serve-low-latency-features-from-an-online-feature-store.md)
* [Run replicated stateless scoring instances](0003-run-replicated-stateless-scoring-instances.md)
* [Record model version and feature snapshot with each score](0004-record-model-version-and-feature-snapshot-with-each-score.md)

## Decisions left open

* Fraud threshold and how scores affect authorization outcomes
* Exact latency target and timeout behavior
* Feature definitions, source systems, and freshness targets
* Model training, validation, approval, and deployment process
* Behavior when scoring or feature dependencies are unavailable
* Audit record retention, access controls, and data privacy requirements
* Deployment environment, regions, and recovery objectives
