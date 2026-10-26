# Architecture decisions: Card-fraud scoring service

* [Microservice based model serving](0001-microservice-based-model-serving.md)
* [Feature store](0002-feature-store.md)
* [Model in-production tracking](0003-model-in-production-tracking.md)
* [N versions in production](0004-n-versions-in-production.md)

## Decisions left open

* Scoring timeout, fallback, and authorization behavior
* Latency and availability targets and recovery design
* Feature source, retention, and historical reconstruction policy
* Audit record retention, access controls, and privacy rules
* Model training, validation, approval, and release criteria
* Fraud threshold and decision policy
