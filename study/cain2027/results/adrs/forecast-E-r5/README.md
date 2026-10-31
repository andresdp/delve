# Architecture decisions: Retail demand forecasting

* [Use a data version repository to reproduce historical forecasts](0001-use-a-data-version-repository-to-reproduce-historical-foreca.md)
* [Use scheduled batch processing and training for weekly forecasts](0002-use-scheduled-batch-processing-and-training-for-weekly-forec.md)
* [Serve forecasts as scheduled batch outputs](0003-serve-forecasts-as-scheduled-batch-outputs.md)
* [Use CI/CD to test and release model components](0004-use-ci-cd-to-test-and-release-model-components.md)
* [Keep rollback available and track deployed models](0005-keep-rollback-available-and-track-deployed-models.md)

## Decisions left open

* How to define forecast quality thresholds and promotion criteria for this retailer.
* How to store and retain forecast outputs and model artifacts across past weeks.
* How to handle missing data, late-arriving data, and corrections to historical inputs.
* How to schedule retries, alert owners, and recover from a failed weekly run.
* How to govern access to retail data and forecast outputs.
