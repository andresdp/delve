# Architecture decisions: Card-fraud scoring service

* [Score synchronously before authorization](0001-score-synchronously-before-authorization.md)
* [Scale scoring with stateless replicas](0002-scale-scoring-with-stateless-replicas.md)
* [Record score-time model and feature inputs](0003-record-score-time-model-and-feature-inputs.md)

## Decisions left open

* Model family and training approach
* Feature definitions and sources
* Model rollout and rollback policy
* Timeout and fallback behavior when scoring is unavailable
* Record retention period and access controls
* Deployment platform and capacity targets
