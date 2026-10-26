# Architecture decisions: Retail demand forecasting

* [main requirements in priority order](0001-main-requirements-in-priority-order.md)
* [how should workflow steps run](0002-how-should-workflow-steps-run.md)
* [how should historical forecasts be reproducible](0003-how-should-historical-forecasts-be-reproducible.md)
* [how should model releases protect the weekly run](0004-how-should-model-releases-protect-the-weekly-run.md)
* [how should candidate models be evaluated before promotion](0005-how-should-candidate-models-be-evaluated-before-promotion.md)

## Not grounded in the design space

* How to set forecast accuracy targets and business-specific evaluation metrics.
* How long to retain historical input data and run artifacts.
* How to monitor forecast quality and trigger retraining or rollback.
