# Architecture decisions: Card-fraud scoring service

* [prediction serving interface](0001-prediction-serving-interface.md)
* [serving capacity and scaling](0002-serving-capacity-and-scaling.md)
* [serving deployment placement](0003-serving-deployment-placement.md)
* [model and feature audit traceability](0004-model-and-feature-audit-traceability.md)
* [production monitoring](0005-production-monitoring.md)

## Not grounded in the design space

* Exact latency budget, percentile target, and timeout or fallback behavior.
* Peak transaction volume, availability target, and regional failover requirements.
* Per-score feature-value retention, explanation format, and audit retention period.
* Model family, training and evaluation strategy, and promotion criteria.
