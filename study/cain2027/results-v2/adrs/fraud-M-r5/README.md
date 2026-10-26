# Architecture decisions: Card-fraud scoring service

* [prediction serving mode](0001-prediction-serving-mode.md)
* [feature serving storage](0002-feature-serving-storage.md)
* [model and feature lineage](0003-model-and-feature-lineage.md)
* [model runtime placement](0004-model-runtime-placement.md)
* [production service and data monitoring](0005-production-service-and-data-monitoring.md)

## Not grounded in the design space

* Exact latency target and percentile (the brief says only “tens of milliseconds”).
* Peak traffic profile, availability target, and regional failover requirements.
* Score-record schema, retention period, access controls, and audit query workflow.
* Feature snapshot or version capture method for each individual score.
* Fraud decision policy, including thresholds, fallback behavior, and human review.
