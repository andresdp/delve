# Architecture decisions: Large-scale document classification

* [how to ingest incoming documents](0001-how-to-ingest-incoming-documents.md)
* [how to process documents](0002-how-to-process-documents.md)
* [how to serve classification results](0003-how-to-serve-classification-results.md)
* [how to monitor classification quality](0004-how-to-monitor-classification-quality.md)

## Not grounded in the design space

* Autoscaling and capacity planning for seasonal volume.
* Access control and result contracts for consuming teams.
* How to obtain quality labels and set drift thresholds.
* Model update, review, and rollback policy.
