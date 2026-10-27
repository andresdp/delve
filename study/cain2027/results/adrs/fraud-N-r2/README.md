# Architecture decisions: Card-fraud scoring service

* [Score transactions synchronously before authorization](0001-score-transactions-synchronously-before-authorization.md)
* [Scale scoring service instances horizontally](0002-scale-scoring-service-instances-horizontally.md)
* [Serve explicitly versioned models](0003-serve-explicitly-versioned-models.md)
* [Record the feature values used for each score](0004-record-the-feature-values-used-for-each-score.md)
* [Keep an auditable record for every score](0005-keep-an-auditable-record-for-every-score.md)
* [Make scoring capacity independent of individual requests](0006-make-scoring-capacity-independent-of-individual-requests.md)

## Decisions left open

* Feature computation sources, freshness requirements, and online/offline consistency
* Score thresholding and authorization outcomes
* Fallback behavior when scoring or required features are unavailable
* Peak traffic volume, capacity targets, and precise latency budget
* Audit record schema, retention period, and access controls
* Model training, validation, approval, deployment, and rollback process
* Required explanation format and auditor interface
* Data residency, privacy, and security constraints
