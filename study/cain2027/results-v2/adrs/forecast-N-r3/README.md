# Architecture decisions: Retail demand forecasting

* [Run forecasts as a scheduled weekly batch](0001-run-forecasts-as-a-scheduled-weekly-batch.md)
* [Preserve versioned inputs and artifacts for reproducibility](0002-preserve-versioned-inputs-and-artifacts-for-reproducibility.md)
* [Validate model changes before the weekly production run](0003-validate-model-changes-before-the-weekly-production-run.md)

## Decisions left open

* Forecast accuracy targets and evaluation metrics
* Data sources, quality checks, and historical data retention period
* Forecast delivery format, consumers, and delivery deadline
* Infrastructure, orchestration, monitoring, and recovery requirements
* Model ownership and production promotion authority
