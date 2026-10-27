# Architecture decisions: Large-scale document classification

* [Use batched ingestion for incoming documents](0001-use-batched-ingestion-for-incoming-documents.md)
* [Partition batches to parallelize document processing](0002-partition-batches-to-parallelize-document-processing.md)
* [Serve classifications through batch prediction](0003-serve-classifications-through-batch-prediction.md)
* [Integrate the classifier as an event-driven service](0004-integrate-the-classifier-as-an-event-driven-service.md)
* [Monitor model performance in production](0005-monitor-model-performance-in-production.md)
* [Use manual model adjustment after drift review](0006-use-manual-model-adjustment-after-drift-review.md)

## Decisions left open

* Document storage, retention, and access control
* Result notification and delivery contract for consuming teams
* Quality metrics, drift thresholds, and ground-truth feedback
* Model training, retraining cadence, and version promotion
* Seasonal capacity provisioning and failure recovery
* Security, privacy, and audit requirements for insurer documents
