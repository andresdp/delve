# Architecture decisions: Large-scale document classification

* [how should classification predictions be served](0001-how-should-classification-predictions-be-served.md)
* [how should incoming documents be processed](0002-how-should-incoming-documents-be-processed.md)
* [how should processing scale across the document workload](0003-how-should-processing-scale-across-the-document-workload.md)
* [how should classification quality be monitored](0004-how-should-classification-quality-be-monitored.md)

## Not grounded in the design space

* How to obtain timely ground truth or other feedback for measuring classification quality.
* Latency and freshness targets for results consumed by teams.
* Document retention, privacy, and access controls for an insurer's data.
* LLM selection, prompt or model version management, and fallback behavior.
* Team-facing result schema, delivery contract, and failure handling.
* Seasonal capacity limits and cost targets.
