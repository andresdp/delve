# Architecture decisions: Large-scale document classification

* [how should documents enter the system](0001-how-should-documents-enter-the-system.md)
* [should documents be processed in batches or in real time](0002-should-documents-be-processed-in-batches-or-in-real-time.md)
* [how should processing scale across documents](0003-how-should-processing-scale-across-documents.md)
* [how should predictions be served](0004-how-should-predictions-be-served.md)
* [how should shared results be stored](0005-how-should-shared-results-be-stored.md)
* [how should production quality be monitored](0006-how-should-production-quality-be-monitored.md)

## Not grounded in the design space

* How to define classification quality metrics and drift thresholds.
* How to manage document privacy, retention, and access controls.
* How to select, prompt, evaluate, and update the LLM classifier.
* How consumers discover results and handle failed or delayed batches.
* How to provision elastic capacity and meet latency or availability targets.
