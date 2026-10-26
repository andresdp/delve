# Architecture decisions: Large-scale document classification

* [Data ingestion in batches](0001-data-ingestion-in-batches.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Data partitioning in data pipeline](0003-data-partitioning-in-data-pipeline.md)
* [Data batch based model serving](0004-data-batch-based-model-serving.md)
* [Model performance monitoring](0005-model-performance-monitoring.md)

## Decisions left open

* How results are stored, versioned, and exposed consistently to several teams.
* How classification quality is measured when ground-truth labels become available.
* How to scale compute and control cost during seasonal peaks.
* Model choice, retraining cadence, and human review for uncertain classifications.
* Security, privacy, retention, audit, and regulatory controls for insurer documents.
