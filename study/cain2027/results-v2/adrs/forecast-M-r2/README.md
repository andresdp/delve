# Architecture decisions: Retail demand forecasting

* [Orchestrated ML pipeline](0001-orchestrated-ml-pipeline.md)
* [Progressive release automation with rollback](0002-progressive-release-automation-with-rollback.md)
* [End-to-end reproducible lifecycle governance](0003-end-to-end-reproducible-lifecycle-governance.md)
* [Threshold-based quality regression testing](0004-threshold-based-quality-regression-testing.md)
* [Scheduled batch prediction deployment](0005-scheduled-batch-prediction-deployment.md)

## Decisions left open

* Data ingestion source and mechanism; the brief does not identify upstream systems or delivery patterns.
* Forecasting model family, training and tuning strategy, and the business metric used to select candidates.
* Dataset retention period and the exact data, code, dependency, and environment snapshot needed to reproduce any past week.
* Forecast delivery interface and downstream consumers.
* Operational monitoring signals, alert thresholds, and ownership of weekly-run recovery.
