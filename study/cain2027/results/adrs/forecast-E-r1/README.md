# Architecture decisions: Retail demand forecasting

* [Version forecast inputs in a data version repository](0001-version-forecast-inputs-in-a-data-version-repository.md)
* [Process retail demand in weekly batches](0002-process-retail-demand-in-weekly-batches.md)
* [Train models with batch-based learning](0003-train-models-with-batch-based-learning.md)
* [Use a CI/CD pipeline for model delivery](0004-use-a-ci-cd-pipeline-for-model-delivery.md)
* [Keep one model version in production and retain rollback](0005-keep-one-model-version-in-production-and-retain-rollback.md)
* [Gate model promotion on trained model quality](0006-gate-model-promotion-on-trained-model-quality.md)
* [Monitor model performance in production](0007-monitor-model-performance-in-production.md)

## Decisions left open

* Forecast quality metric and acceptance threshold.
* Historical data sources, schema contracts, and late data policy.
* Weekly scheduling, failure recovery, and rerun semantics.
* Forecast output interface and consuming systems.
* Retention and access controls for input snapshots, predictions, and model artifacts.
* Model family, feature design, and hyperparameter selection.
