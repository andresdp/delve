# Architecture decisions: Retail demand forecasting

* [Store × product × week](0001-store-product-week.md)
* [Scheduled batch run with isolated experiments](0002-scheduled-batch-run-with-isolated-experiments.md)
* [Versioned inputs, code, configuration, and model artifacts](0003-versioned-inputs-code-configuration-and-model-artifacts.md)
* [Promote a validated model version between runs](0004-promote-a-validated-model-version-between-runs.md)

## Decisions left open

* Forecast horizon and whether forecasts are generated one or multiple weeks ahead.
* Demand definition, source systems, data quality rules, and late-arriving data policy.
* Accuracy metrics, acceptance thresholds, and model selection criteria.
* Required forecast delivery format, consumers, and availability deadline.
* Runtime, hosting, access control, monitoring, alerting, and recovery requirements.
* Retention period and exact replay expectations when historical source data changes.
