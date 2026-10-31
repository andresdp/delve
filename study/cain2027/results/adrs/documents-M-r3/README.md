# Architecture decisions: Large-scale document classification

* [Use scheduled batch scoring for document classification](0001-use-scheduled-batch-scoring-for-document-classification.md)
* [Monitor classification quality and input drift in production](0002-monitor-classification-quality-and-input-drift-in-production.md)
* [Scale classification resources elastically](0003-scale-classification-resources-elastically.md)
* [Expose classification results through a REST prediction microservice](0004-expose-classification-results-through-a-rest-prediction-micr.md)

## Decisions left open

* LLM provider, model choice, and model-version governance
* Document intake and storage design
* Classification label taxonomy and confidence or abstention policy
* Access control and retention for insurer documents
* Batch cadence, recovery, and duplicate handling
* How results are published to consuming teams
* Quality thresholds and drift alert escalation
* Human review and retraining approval policy
