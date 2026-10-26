# Architecture decisions: Card-fraud scoring service

* [how to serve fraud scores](0001-how-to-serve-fraud-scores.md)
* [how to persist and provide access to features](0002-how-to-persist-and-provide-access-to-features.md)
* [how to track model use in production](0003-how-to-track-model-use-in-production.md)
* [how many model versions should run in production](0004-how-many-model-versions-should-run-in-production.md)

## Not grounded in the design space

* Scoring timeout, fallback, and authorization behavior
* Latency and availability targets and recovery design
* Feature source, retention, and historical reconstruction policy
* Audit record retention, access controls, and privacy rules
* Model training, validation, approval, and release criteria
* Fraud threshold and decision policy
