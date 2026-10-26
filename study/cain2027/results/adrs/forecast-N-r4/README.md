# Architecture decisions: Retail demand forecasting

* [Scheduled staged pipeline](0001-scheduled-staged-pipeline.md)
* [Versioned run snapshots](0002-versioned-run-snapshots.md)
* [Isolated candidate evaluation with promotion](0003-isolated-candidate-evaluation-with-promotion.md)
* [Versioned forecast table](0004-versioned-forecast-table.md)

## Decisions left open

* Source systems, data quality rules, and late or corrected data handling.
* Forecast horizon, required accuracy, evaluation metrics, and baseline.
* Infrastructure, orchestration technology, storage platform, and deployment environment.
* Consumer requirements, access controls, and forecast delivery timing.
* Run failure service levels, alerting ownership, and artifact retention period.
