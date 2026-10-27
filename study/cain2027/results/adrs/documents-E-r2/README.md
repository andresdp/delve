# Architecture decisions: Large-scale document classification

* [Use batch serving for document classification](0001-use-batch-serving-for-document-classification.md)
* [Ingest documents in batches](0002-ingest-documents-in-batches.md)
* [Partition batch processing to scale throughput](0003-partition-batch-processing-to-scale-throughput.md)
* [Monitor model performance and log predictions](0004-monitor-model-performance-and-log-predictions.md)

## Decisions left open

* How consumers discover and retrieve completed results, including notification or polling behavior.
* How to define, measure, and alert on classification quality drift, including ground-truth availability and thresholds.
* How to manage privacy, security, and retention for insurer documents and predictions.
* How to handle failures, retries, duplicate documents, and processing deadlines.
* How to choose, evaluate, and update the LLM classifier and its claim-type taxonomy.
* How to scale compute and control costs during seasonal peaks.
