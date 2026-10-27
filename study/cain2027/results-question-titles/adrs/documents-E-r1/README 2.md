# Architecture decisions: Large-scale document classification

* [how should the classifier integrate with the application](0001-how-should-the-classifier-integrate-with-the-application.md)
* [how should predictions be served](0002-how-should-predictions-be-served.md)
* [how should incoming documents be ingested and processed](0003-how-should-incoming-documents-be-ingested-and-processed.md)
* [how should data processing be parallelized](0004-how-should-data-processing-be-parallelized.md)
* [where should documents and results be stored](0005-where-should-documents-and-results-be-stored.md)
* [how should consumers learn that results are ready](0006-how-should-consumers-learn-that-results-are-ready.md)
* [how should classification quality be monitored](0007-how-should-classification-quality-be-monitored.md)

## Not grounded in the design space

* Document privacy, security, and regulatory controls.
* Storage technology, retention, and deletion rules.
* Model evaluation method, quality thresholds, and drift detection approach.
* LLM provider, model choice, prompt management, and fallback behavior.
* Batch schedule, latency targets, retry policy, and failure recovery.
* Consumer result schema, access control, and notification protocol.
* Seasonal capacity targets, scaling policy, and cost limits.
