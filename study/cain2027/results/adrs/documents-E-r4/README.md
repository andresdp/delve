# Architecture decisions: Large-scale document classification

* [Use batch based serving for document classifications](0001-use-batch-based-serving-for-document-classifications.md)
* [Ingest documents in batches](0002-ingest-documents-in-batches.md)
* [Store inputs and predictions in a shared data store](0003-store-inputs-and-predictions-in-a-shared-data-store.md)
* [Notify clients by polling for completed results](0004-notify-clients-by-polling-for-completed-results.md)
* [Monitor model performance in production](0005-monitor-model-performance-in-production.md)
* [Review drift before adjusting the model](0006-review-drift-before-adjusting-the-model.md)

## Decisions left open

* LLM selection, hosting, prompt design, and classifier output schema
* Document privacy, security, retention, and audit requirements
* Capacity planning, autoscaling, and seasonal peak handling
* Batch cadence, retry behavior, deduplication, and failure recovery
* Team access controls and result ownership
* Ground truth collection, drift thresholds, and alert routing
* Model validation, release approval, rollback, and retraining workflow
