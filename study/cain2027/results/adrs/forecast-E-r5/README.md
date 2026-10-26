# Architecture decisions: Retail demand forecasting

* [how should weekly demand data be processed](0001-how-should-weekly-demand-data-be-processed.md)
* [how should historical data be versioned](0002-how-should-historical-data-be-versioned.md)
* [when and how should the model be trained](0003-when-and-how-should-the-model-be-trained.md)
* [how should forecasts be delivered](0004-how-should-forecasts-be-delivered.md)
* [how should changes reach production safely](0005-how-should-changes-reach-production-safely.md)
* [how should deployed model quality be monitored and recovered](0006-how-should-deployed-model-quality-be-monitored-and-recovered.md)

## Not grounded in the design space

* Forecasting algorithm and model selection criteria.
* Forecast schedule, cut-off times, and late-arriving data handling.
* Storage technology, schema, and retention for inputs and forecast outputs.
* Evaluation metrics and acceptable quality thresholds.
* Rollout procedure and specific recovery trigger.
