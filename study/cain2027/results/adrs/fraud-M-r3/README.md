# Architecture decisions: Card-fraud scoring service

* [prediction serving mode](0001-prediction-serving-mode.md)
* [prediction service interface](0002-prediction-service-interface.md)
* [serving state and scaling](0003-serving-state-and-scaling.md)
* [runtime capacity strategy](0004-runtime-capacity-strategy.md)
* [production monitoring](0005-production-monitoring.md)
* [model and feature traceability](0006-model-and-feature-traceability.md)
* [online and durable feature storage](0007-online-and-durable-feature-storage.md)

## Not grounded in the design space

* Score retention period, privacy controls, and audit access policy.
* Feature retrieval timeout and degraded-mode behavior.
* Fraud labels, evaluation metrics, alert thresholds, and model promotion policy.
* Deployment topology, regional failover, and recovery objectives.
