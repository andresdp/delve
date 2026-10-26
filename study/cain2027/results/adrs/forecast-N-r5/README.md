# Architecture decisions: Retail demand forecasting

* [what is the forecast grain](0001-what-is-the-forecast-grain.md)
* [how should weekly runs be scheduled and isolated](0002-how-should-weekly-runs-be-scheduled-and-isolated.md)
* [what must be recorded to reproduce a past forecast](0003-what-must-be-recorded-to-reproduce-a-past-forecast.md)
* [how should model ideas reach production](0004-how-should-model-ideas-reach-production.md)

## Not grounded in the design space

* Forecast horizon and whether forecasts are generated one or multiple weeks ahead.
* Demand definition, source systems, data quality rules, and late-arriving data policy.
* Accuracy metrics, acceptance thresholds, and model selection criteria.
* Required forecast delivery format, consumers, and availability deadline.
* Runtime, hosting, access control, monitoring, alerting, and recovery requirements.
* Retention period and exact replay expectations when historical source data changes.
