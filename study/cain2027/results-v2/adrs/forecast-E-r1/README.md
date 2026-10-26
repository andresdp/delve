# Architecture decisions: Retail demand forecasting

* [Version data used for each forecast](0001-version-data-used-for-each-forecast.md)
* [Batch-based data processing](0002-batch-based-data-processing.md)
* [Model building pipeline with batch-based learning](0003-model-building-pipeline-with-batch-based-learning.md)
* [Precompute serving](0004-precompute-serving.md)
* [CI/CD pipeline with rollback to previous model version](0005-ci-cd-pipeline-with-rollback-to-previous-model-version.md)
* [Integration testing pipeline components](0006-integration-testing-pipeline-components.md)

## Decisions left open

* Prioritized brief requirements: reproducibility of any past week; weekly run reliability; fast production iteration; small-team maintainability.
* How long to retain historical data, models, and forecast artifacts, and how to reproduce a past run end to end.
* Forecast accuracy metrics and release thresholds for model-quality tests.
* The brief does not specify forecast consumers, delivery format, or access controls.
* Operational monitoring, alerting, and ownership for failed or delayed weekly runs.
