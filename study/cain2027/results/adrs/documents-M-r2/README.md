# Architecture decisions: Large-scale document classification

* [Use streaming feature ingestion for document intake](0001-use-streaming-feature-ingestion-for-document-intake.md)
* [Use an orchestrated ML pipeline for repeatable model operations](0002-use-an-orchestrated-ml-pipeline-for-repeatable-model-operati.md)
* [Expose classification through a REST prediction microservice](0003-expose-classification-through-a-rest-prediction-microservice.md)
* [Monitor input drift and model quality in production](0004-monitor-input-drift-and-model-quality-in-production.md)
* [Evaluate candidate models offline before promotion](0005-evaluate-candidate-models-offline-before-promotion.md)

## Decisions left open

* Synchronous or asynchronous result delivery and delivery guarantees for consuming teams.
* Seasonal capacity, queueing, and cost strategy for the classification service.
* LLM provider, model choice, prompt or version management, and inference limits.
* Label acquisition and ground-truth timing for measuring classification quality.
* Claim-type error costs, quality thresholds, fairness, privacy, and retention requirements.
* Security, access control, and audit requirements for insurer documents and predictions.
