# Architecture decisions: Card-fraud scoring service

* [Synchronous in-process model scoring](0001-synchronous-in-process-model-scoring.md)
* [Replicated stateless instances with autoscaling](0002-replicated-stateless-instances-with-autoscaling.md)
* [Persist score, model version, and feature snapshot](0003-persist-score-model-version-and-feature-snapshot.md)
* [Deploy immutable, versioned model artifacts](0004-deploy-immutable-versioned-model-artifacts.md)

## Decisions left open

* Feature generation and source-of-truth design
* Feature freshness and missing-data behavior
* Model training, validation, and approval process
* Audit record retention duration and privacy constraints
* Capacity targets, failure objectives, and overload behavior
* Score thresholding and authorization policy
