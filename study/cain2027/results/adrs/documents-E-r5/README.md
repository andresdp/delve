# Architecture decisions: Large-scale document classification

* [how should documents be ingested](0001-how-should-documents-be-ingested.md)
* [should documents be processed in batches or in real time](0002-should-documents-be-processed-in-batches-or-in-real-time.md)
* [how should data processing be parallelized](0003-how-should-data-processing-be-parallelized.md)
* [how should predictions be served to consuming teams](0004-how-should-predictions-be-served-to-consuming-teams.md)
* [how should production classification quality be monitored](0005-how-should-production-classification-quality-be-monitored.md)

## Not grounded in the design space

* How results are stored, versioned, and exposed consistently to several teams.
* How classification quality is measured when ground-truth labels become available.
* How to scale compute and control cost during seasonal peaks.
* Model choice, retraining cadence, and human review for uncertain classifications.
* Security, privacy, retention, audit, and regulatory controls for insurer documents.
