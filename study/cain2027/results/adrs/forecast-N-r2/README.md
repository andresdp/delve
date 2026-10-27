# Architecture decisions: Retail demand forecasting

* [Version input data and code for reproducible weekly forecasts](0001-version-input-data-and-code-for-reproducible-weekly-forecast.md)
* [Separate model experiments from the weekly production run](0002-separate-model-experiments-from-the-weekly-production-run.md)
* [Make the weekly forecast pipeline a single team-owned workflow](0003-make-the-weekly-forecast-pipeline-a-single-team-owned-workfl.md)

## Decisions left open

* Forecast serving and delivery interface
* Forecast horizon and required output schema
* Data sources, quality rules, and late-arriving data policy
* Evaluation metrics and candidate promotion thresholds
* Retraining cadence and model rollback policy
* Runtime, cloud, security, and availability constraints
