# Architecture decisions: Retail demand forecasting

* [how should weekly runs be coordinated](0001-how-should-weekly-runs-be-coordinated.md)
* [how should past forecasts be reproducible](0002-how-should-past-forecasts-be-reproducible.md)
* [how should model changes be released](0003-how-should-model-changes-be-released.md)
* [how should candidate forecasts be evaluated](0004-how-should-candidate-forecasts-be-evaluated.md)
* [how should source data be preserved](0005-how-should-source-data-be-preserved.md)

## Not grounded in the design space

* Forecasting model family and seasonal or calendar feature strategy.
* Historical data storage and retrieval design, including retention duration.
* Forecast publication interface and consumer access patterns.
* Compute platform, deployment environment, and recovery objectives.
* Forecast quality metric definitions and acceptable thresholds.
