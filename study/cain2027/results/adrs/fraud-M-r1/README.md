# Architecture decisions: Card-fraud scoring service

* [prediction serving mode](0001-prediction-serving-mode.md)
* [model serving interface](0002-model-serving-interface.md)
* [serving instance state and scaling](0003-serving-instance-state-and-scaling.md)
* [online feature serving](0004-online-feature-serving.md)
* [model and feature audit traceability](0005-model-and-feature-audit-traceability.md)
* [production monitoring](0006-production-monitoring.md)

## Not grounded in the design space

* Per-transaction audit event schema, retention period, and access controls.
* Scoring timeout, feature-store failure, and authorization fallback behavior.
* Transaction data ingestion and feature freshness guarantees.
* Fraud model family, score calibration, decision thresholds, and human review.
* Deployment topology, regional failover, capacity targets, and service-level objectives.
