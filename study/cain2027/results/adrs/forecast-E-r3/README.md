# Architecture decisions: Retail demand forecasting

* [how should demand data be processed](0001-how-should-demand-data-be-processed.md)
* [how should forecast results be served](0002-how-should-forecast-results-be-served.md)
* [how should historical inputs be reproduced](0003-how-should-historical-inputs-be-reproduced.md)
* [how should the weekly workflow run](0004-how-should-the-weekly-workflow-run.md)
* [how should training fit the workflow](0005-how-should-training-fit-the-workflow.md)
* [what should the model building pipeline do](0006-what-should-the-model-building-pipeline-do.md)
* [how should changes reach production](0007-how-should-changes-reach-production.md)
* [what should be tested before accepting a model](0008-what-should-be-tested-before-accepting-a-model.md)
* [how should production model versions be managed](0009-how-should-production-model-versions-be-managed.md)
* [how should production forecasts be monitored](0010-how-should-production-forecasts-be-monitored.md)
* [how should monitoring results change models](0011-how-should-monitoring-results-change-models.md)

## Not grounded in the design space

* Forecast consumers and output interface
* Storage and retention of forecast artifacts
* Feature and label definitions for store-product demand
* Forecast quality metrics and promotion thresholds
* Ownership and alerting for failed weekly runs
* Access control and data privacy
* Recovery time and retention targets
