# Architecture decisions: Large-scale document classification

* [how should documents be ingested](0001-how-should-documents-be-ingested.md)
* [should data be processed in batches or in real time](0002-should-data-be-processed-in-batches-or-in-real-time.md)
* [how should data processing be parallelized](0003-how-should-data-processing-be-parallelized.md)
* [how should model quality be monitored in production](0004-how-should-model-quality-be-monitored-in-production.md)
* [how should predictions be served to consuming teams](0005-how-should-predictions-be-served-to-consuming-teams.md)

## Not grounded in the design space

* Business latency target and batch cadence
* Document and prediction storage, retention, and access controls
* How teams discover and retrieve results
* Quality metric, source of ground truth, and drift thresholds
* Whether monitoring should trigger human review, retraining, or model replacement
