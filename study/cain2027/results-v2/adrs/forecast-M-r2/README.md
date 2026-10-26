# Architecture decisions: Retail demand forecasting

* [workflow execution orchestrated pipeline or manual scripts](0001-workflow-execution-orchestrated-pipeline-or-manual-scripts.md)
* [how should model and pipeline changes be released](0002-how-should-model-and-pipeline-changes-be-released.md)
* [how should past week forecasts be reproducible](0003-how-should-past-week-forecasts-be-reproducible.md)
* [how should candidate models be checked before promotion](0004-how-should-candidate-models-be-checked-before-promotion.md)
* [when should forecasts be computed](0005-when-should-forecasts-be-computed.md)

## Not grounded in the design space

* Data ingestion source and mechanism; the brief does not identify upstream systems or delivery patterns.
* Forecasting model family, training and tuning strategy, and the business metric used to select candidates.
* Dataset retention period and the exact data, code, dependency, and environment snapshot needed to reproduce any past week.
* Forecast delivery interface and downstream consumers.
* Operational monitoring signals, alert thresholds, and ownership of weekly-run recovery.
