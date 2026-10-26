# Architecture decisions: Card-fraud scoring service

* [model integration](0001-model-integration.md)
* [online score serving](0002-online-score-serving.md)
* [feature persistence and access](0003-feature-persistence-and-access.md)
* [production model version changes](0004-production-model-version-changes.md)
* [versioning data used for model work](0005-versioning-data-used-for-model-work.md)
* [production model tracking](0006-production-model-tracking.md)
* [prediction service performance testing](0007-prediction-service-performance-testing.md)

## Not grounded in the design space

* High-availability topology and failure recovery for the scoring service
* Behavior when scoring times out or feature retrieval fails
* Audit record retention, integrity, and access controls
* Transaction and feature data privacy requirements
* Capacity targets and autoscaling policy
* Model explainability method and explanation format
* Fraud model training cadence and approval process
