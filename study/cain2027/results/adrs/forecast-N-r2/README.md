# Architecture decisions: Retail demand forecasting

* [how should forecasting run](0001-how-should-forecasting-run.md)
* [how should past forecasts be reproduced](0002-how-should-past-forecasts-be-reproduced.md)
* [how should model ideas reach production](0003-how-should-model-ideas-reach-production.md)

## Not grounded in the design space

* Forecast horizon and required output format.
* Source systems, input schema, and late or corrected data policy.
* Forecast accuracy targets and model evaluation metrics.
* Serving or downstream delivery requirements.
* Runtime, deployment environment, and operational ownership beyond the three data scientists.
* Retention duration and exact reproducibility guarantees.
