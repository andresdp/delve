# Architecture decisions: Card-fraud scoring service

* [Prediction serving mode](0001-prediction-serving-mode.md)
* [Prediction service interface](0002-prediction-service-interface.md)
* [Serving state and scaling](0003-serving-state-and-scaling.md)
* [Runtime capacity strategy](0004-runtime-capacity-strategy.md)
* [Production monitoring](0005-production-monitoring.md)
* [Model and feature traceability](0006-model-and-feature-traceability.md)
* [Online and durable feature storage](0007-online-and-durable-feature-storage.md)

## Decisions left open

* Score retention period, privacy controls, and audit access policy.
* Feature retrieval timeout and degraded-mode behavior.
* Fraud labels, evaluation metrics, alert thresholds, and model promotion policy.
* Deployment topology, regional failover, and recovery objectives.
