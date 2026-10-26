# Architecture decisions: Card-fraud scoring service

* [Prediction serving interface](0001-prediction-serving-interface.md)
* [Serving capacity and scaling](0002-serving-capacity-and-scaling.md)
* [Serving deployment placement](0003-serving-deployment-placement.md)
* [Model and feature audit traceability](0004-model-and-feature-audit-traceability.md)
* [Production monitoring](0005-production-monitoring.md)

## Decisions left open

* Exact latency budget, percentile target, and timeout or fallback behavior.
* Peak transaction volume, availability target, and regional failover requirements.
* Per-score feature-value retention, explanation format, and audit retention period.
* Model family, training and evaluation strategy, and promotion criteria.
