# Architecture decisions: Large-scale document classification

* [Use batch ingestion for incoming documents](0001-use-batch-ingestion-for-incoming-documents.md)
* [Combine batch and online prediction serving](0002-combine-batch-and-online-prediction-serving.md)
* [Notify consumers when results are ready](0003-notify-consumers-when-results-are-ready.md)
* [Partition data processing to handle volume variation](0004-partition-data-processing-to-handle-volume-variation.md)
* [Monitor model performance in production](0005-monitor-model-performance-in-production.md)

## Decisions left open

* How to measure classification quality and detect drift when ground-truth labels arrive late or sparsely.
* How to choose, evaluate, update, and roll back the LLM classifier.
* How to protect sensitive insurance documents and control team access to results.
* How to store, retain, and version documents, predictions, and model configurations.
* Capacity, latency, availability, and cost targets for seasonal peaks.
