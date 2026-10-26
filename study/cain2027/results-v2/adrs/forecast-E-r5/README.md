# Architecture decisions: Retail demand forecasting

* [Data version repository](0001-data-version-repository.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [CI/CD pipeline](0004-ci-cd-pipeline.md)
* [Integration testing pipeline components](0005-integration-testing-pipeline-components.md)
* [Model performance monitoring](0006-model-performance-monitoring.md)

## Decisions left open

* Forecast quality metrics and acceptance thresholds.
* How model versions are promoted or rolled back safely.
* Storage and access design for forecasts by store and product.
* Operational ownership and response to failed weekly runs.
