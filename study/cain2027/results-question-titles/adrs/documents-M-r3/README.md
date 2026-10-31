# Architecture decisions: Large-scale document classification

* [Scheduled batch prediction deployment](0001-scheduled-batch-prediction-deployment.md)
* [Elastic resource scaling](0002-elastic-resource-scaling.md)
* [Real-time prediction-quality monitoring](0003-real-time-prediction-quality-monitoring.md)
* [Input and feature-drift monitoring](0004-input-and-feature-drift-monitoring.md)

## Decisions left open

* LLM model selection, hosting, token limits, and inference cost.
* Document ingestion format, source integration, and queueing or retry policy.
* Result schema, access controls, and delivery contract for consuming teams.
* Batch cadence, freshness target, and service-level objectives.
