# Architecture decisions: Large-scale document classification

* [Batch-based data processing](0001-batch-based-data-processing.md)
* [Data batch based model serving](0002-data-batch-based-model-serving.md)
* [Shared data store](0003-shared-data-store.md)
* [Model performance monitoring](0004-model-performance-monitoring.md)
* [Data version repository](0005-data-version-repository.md)
* [Manual model adjustment](0006-manual-model-adjustment.md)

## Decisions left open

* Per-document latency target and batch completion objective
* Quality metric, drift threshold, and alert routing
* Input and result retention, privacy, and access controls
* Model selection, training cadence, and validation criteria
* Seasonal capacity targets and recovery objectives
