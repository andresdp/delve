# Architecture decisions: Large-scale document classification

* [Elastic resource scaling](0001-elastic-resource-scaling.md)
* [Streaming feature ingestion](0002-streaming-feature-ingestion.md)
* [Scheduled batch prediction deployment](0003-scheduled-batch-prediction-deployment.md)
* [Asynchronous message-driven serving](0004-asynchronous-message-driven-serving.md)
* [REST prediction microservice](0005-rest-prediction-microservice.md)
* [Combined quality and input-drift monitoring](0006-combined-quality-and-input-drift-monitoring.md)
* [Orchestrated ML pipeline](0007-orchestrated-ml-pipeline.md)

## Decisions left open

* LLM provider, model choice, and inference cost controls.
* Claim taxonomy, confidence thresholds, and fallback handling.
* Label collection and ground-truth timing for quality measurement.
* Retention, privacy, and access controls for insurance documents.
* Consumer-specific freshness, availability, and delivery guarantees.
