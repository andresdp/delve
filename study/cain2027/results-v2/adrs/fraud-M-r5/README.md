# Architecture decisions: Card-fraud scoring service

* [Prediction serving mode](0001-prediction-serving-mode.md)
* [Feature serving storage](0002-feature-serving-storage.md)
* [Model and feature lineage](0003-model-and-feature-lineage.md)
* [Model runtime placement](0004-model-runtime-placement.md)
* [Production service and data monitoring](0005-production-service-and-data-monitoring.md)

## Decisions left open

* Exact latency target and percentile (the brief says only “tens of milliseconds”).
* Peak traffic profile, availability target, and regional failover requirements.
* Score-record schema, retention period, access controls, and audit query workflow.
* Feature snapshot or version capture method for each individual score.
* Fraud decision policy, including thresholds, fallback behavior, and human review.
