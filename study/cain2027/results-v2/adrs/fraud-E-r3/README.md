# Architecture decisions: Card-fraud scoring service

* [Microservice based model serving](0001-microservice-based-model-serving.md)
* [Feature store](0002-feature-store.md)
* [Data version repository](0003-data-version-repository.md)
* [Rollback to previous model version](0004-rollback-to-previous-model-version.md)
* [Model in-production tracking](0005-model-in-production-tracking.md)

## Decisions left open

* Peak-load capacity targets, scaling policy, and overload behavior.
* Score latency budget allocation, timeout behavior, and authorization fallback.
* Feature snapshot format, audit retention period, and sensitive-data controls.
* Model quality acceptance criteria and release approval process.
