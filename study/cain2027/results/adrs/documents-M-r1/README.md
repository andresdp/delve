# Architecture decisions: Large-scale document classification

* [Use scheduled batch scoring for document classification](0001-use-scheduled-batch-scoring-for-document-classification.md)
* [Scale classification resources elastically with demand](0002-scale-classification-resources-elastically-with-demand.md)
* [Expose classification results through a REST prediction microservice](0003-expose-classification-results-through-a-rest-prediction-micr.md)
* [Monitor input drift and prediction quality in production](0004-monitor-input-drift-and-prediction-quality-in-production.md)

## Decisions left open

* LLM provider, model selection, and prompt or model versioning.
* Label acquisition and ground-truth timing for quality measurement.
* Classification accuracy targets and drift alert thresholds.
* Privacy, retention, and access controls for insurance documents.
* Batch cadence, freshness objectives, and backlog recovery targets.
* Result storage, ownership, and delivery contracts for consuming teams.
* Human review and escalation for uncertain or consequential classifications. Design-point checks were novel and unattested: the proposed combination returned no attested sources or warnings; a rival combination using queued online serving, vertically scalable training, and passive operation was also unattested.
