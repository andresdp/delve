# Architecture decisions: Retail demand forecasting

* [version data used for each forecast](0001-version-data-used-for-each-forecast.md)
* [process weekly data in batches or streams](0002-process-weekly-data-in-batches-or-streams.md)
* [how should model building and training run](0003-how-should-model-building-and-training-run.md)
* [how should forecasts be delivered](0004-how-should-forecasts-be-delivered.md)
* [how should changes reach production safely](0005-how-should-changes-reach-production-safely.md)
* [what should the pipeline test](0006-what-should-the-pipeline-test.md)

## Not grounded in the design space

* Prioritized brief requirements: reproducibility of any past week; weekly run reliability; fast production iteration; small-team maintainability.
* How long to retain historical data, models, and forecast artifacts, and how to reproduce a past run end to end.
* Forecast accuracy metrics and release thresholds for model-quality tests.
* The brief does not specify forecast consumers, delivery format, or access controls.
* Operational monitoring, alerting, and ownership for failed or delayed weekly runs.
