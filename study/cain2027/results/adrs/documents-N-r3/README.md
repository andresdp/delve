# Architecture decisions: Large-scale document classification

* [Use an LLM classifier for claim-type assignment](0001-use-an-llm-classifier-for-claim-type-assignment.md)
* [Scale classification workers horizontally for variable volume](0002-scale-classification-workers-horizontally-for-variable-volum.md)
* [Publish classification results through a shared service interface](0003-publish-classification-results-through-a-shared-service-inte.md)
* [Monitor classification quality for drift](0004-monitor-classification-quality-for-drift.md)

## Decisions left open

* Document ingestion and delivery protocol
* Classification latency and availability targets
* Claim-type taxonomy and confidence handling
* Quality metrics, labeled data, and drift thresholds
* Human review and correction workflow
* Document privacy, retention, and access controls
