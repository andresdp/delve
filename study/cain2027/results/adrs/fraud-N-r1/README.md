# Architecture decisions: Card-fraud scoring service

* [Score transactions synchronously before authorization](0001-score-transactions-synchronously-before-authorization.md)
* [Scale scoring instances horizontally for transaction peaks](0002-scale-scoring-instances-horizontally-for-transaction-peaks.md)
* [Use immutable, versioned model artifacts for scoring](0003-use-immutable-versioned-model-artifacts-for-scoring.md)
* [Record the feature values used for each score](0004-record-the-feature-values-used-for-each-score.md)

## Decisions left open

* Feature definitions, sources, freshness requirements, and whether features are computed inline or retrieved from a feature store
* Score schema, thresholds, and authorization behavior when scoring times out or is unavailable
* Deployment platform, autoscaling policy, redundancy, and recovery targets
* Audit record retention period, access controls, and storage technology
