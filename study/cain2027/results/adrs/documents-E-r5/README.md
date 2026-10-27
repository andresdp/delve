# Architecture decisions: Large-scale document classification

* [Process incoming documents in batches](0001-process-incoming-documents-in-batches.md)
* [Partition data processing to handle volume](0002-partition-data-processing-to-handle-volume.md)
* [Publish predictions through batch serving](0003-publish-predictions-through-batch-serving.md)
* [Monitor model performance in production](0004-monitor-model-performance-in-production.md)
* [Review monitoring results before adjusting models](0005-review-monitoring-results-before-adjusting-models.md)

## Decisions left open

* How classification results are shared and access-controlled across consuming teams.
* How and when classification jobs are triggered and scheduled.
* How document data and prediction results are stored and retained.
* How to define quality measures, detect drift, and alert operators.
