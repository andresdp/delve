# Architecture decisions: Card-fraud scoring service

* [Model as a service](0001-model-as-a-service.md)
* [Microservice based model serving](0002-microservice-based-model-serving.md)
* [Real-time, stream-based data processing](0003-real-time-stream-based-data-processing.md)
* [Feature store](0004-feature-store.md)
* [Data version repository](0005-data-version-repository.md)
* [N versions in production](0006-n-versions-in-production.md)
* [Model in-production tracking](0007-model-in-production-tracking.md)

## Decisions left open

* How to meet the tens-of-milliseconds latency target with a concrete latency budget and timeout policy.
* How to achieve availability targets, including redundancy, failover, and behavior when scoring is unavailable.
* How scores, model versions, and feature inputs are durably linked and retained for auditors.
* How to validate score quality and approve model releases; the design space offers test categories (d:26) but the brief does not specify acceptance criteria.
