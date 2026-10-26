# Architecture decisions: Card-fraud scoring service

* [score synchronously before authorization](0001-score-synchronously-before-authorization.md)
* [scale scoring with stateless replicas](0002-scale-scoring-with-stateless-replicas.md)
* [record score time model and feature inputs](0003-record-score-time-model-and-feature-inputs.md)

## Not grounded in the design space

* Model family and training approach
* Feature definitions and sources
* Model rollout and rollback policy
* Timeout and fallback behavior when scoring is unavailable
* Record retention period and access controls
* Deployment platform and capacity targets
