# Architecture decisions: Large-scale document classification

* [Use a durable queue for bursty document classification](0001-use-a-durable-queue-for-bursty-document-classification.md)
* [Scale stateless classifier workers horizontally](0002-scale-stateless-classifier-workers-horizontally.md)
* [Publish classification results through a shared event stream](0003-publish-classification-results-through-a-shared-event-stream.md)
* [Track classification quality over time](0004-track-classification-quality-over-time.md)

## Decisions left open

* Document ingestion formats and source systems
* Claim-type taxonomy and classification output contract
* Latency and availability targets
* Model choice, hosting, and update strategy
* Privacy, security, and data retention requirements
* Ground-truth source and quality measurement method
* Retry, deduplication, and failure handling semantics
* Consumer access patterns and replay requirements
* Deployment platform and regional requirements
