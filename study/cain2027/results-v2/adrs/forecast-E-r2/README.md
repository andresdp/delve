# Architecture decisions: Retail demand forecasting

* [Prioritize requirements](0001-prioritize-requirements.md)
* [Data version repository](0002-data-version-repository.md)
* [Batch-based learning](0003-batch-based-learning.md)
* [On-schedule trigger](0004-on-schedule-trigger.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [Testing trained model quality](0006-testing-trained-model-quality.md)
* [Rollback to previous model version](0007-rollback-to-previous-model-version.md)

## Decisions left open

* Forecast serving interface and consumers
* Storage format and retention for historical forecasts
* Forecast accuracy metric and acceptance threshold
* Experiment isolation and promotion workflow
* Monitoring, alerting, and ownership for failed weekly runs
* Compute budget and runtime limits
