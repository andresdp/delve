# Architecture decisions: Large-scale document classification

* [how should documents be ingested](0001-how-should-documents-be-ingested.md)
* [should documents be processed in batches or in real time](0002-should-documents-be-processed-in-batches-or-in-real-time.md)
* [how should model predictions be served](0003-how-should-model-predictions-be-served.md)
* [how should data processing scale across the workload](0004-how-should-data-processing-scale-across-the-workload.md)
* [how should production classification quality be monitored](0005-how-should-production-classification-quality-be-monitored.md)

## Not grounded in the design space

* How to establish ground-truth labels and measure classification quality when labels arrive late or are unavailable.
* How to govern claim data, including retention, privacy, access controls, and audit requirements.
* How to version and roll back prompts, models, and classification taxonomies.
* How to handle invalid documents, low-confidence predictions, and human review.
* How to set batch cadence, seasonal capacity targets, latency objectives, and service-level objectives.
* How consuming teams discover and access prediction results and receive availability notifications.
