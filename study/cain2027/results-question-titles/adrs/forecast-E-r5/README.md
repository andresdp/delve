# Architecture decisions: Retail demand forecasting

* [Batch-based data processing](0001-batch-based-data-processing.md)
* [Data version repository](0002-data-version-repository.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [Data batch based model serving](0004-data-batch-based-model-serving.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)

## Decisions left open

* Forecasting algorithm and model selection criteria.
* Forecast schedule, cut-off times, and late-arriving data handling.
* Storage technology, schema, and retention for inputs and forecast outputs.
* Evaluation metrics and acceptable quality thresholds.
* Rollout procedure and specific recovery trigger.
