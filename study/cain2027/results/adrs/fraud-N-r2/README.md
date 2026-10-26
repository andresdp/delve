# Architecture decisions: Card-fraud scoring service

* [how should scoring fit into authorization](0001-how-should-scoring-fit-into-authorization.md)
* [how should the scoring service handle peaks](0002-how-should-the-scoring-service-handle-peaks.md)
* [how should model versions be selected and recorded](0003-how-should-model-versions-be-selected-and-recorded.md)
* [what should be retained for audit explanation](0004-what-should-be-retained-for-audit-explanation.md)

## Not grounded in the design space

* Feature definitions, sources, and computation strategy
* Required audit retention period and access controls
* Timeout, fallback, and authorization behavior when scoring is unavailable
* Deployment platform, peak throughput, and availability targets
* Model training, validation, approval, and rollout process
* Required form of explanation beyond identifying model version and features
