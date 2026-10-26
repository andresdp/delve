# Architecture decisions: Retail demand forecasting

* [Scheduled batch pipeline](0001-scheduled-batch-pipeline.md)
* [Versioned data and model artifacts](0002-versioned-data-and-model-artifacts.md)
* [Separate candidate evaluation and promotion](0003-separate-candidate-evaluation-and-promotion.md)

## Decisions left open

* Forecast horizon and required output format.
* Source systems, input schema, and late or corrected data policy.
* Forecast accuracy targets and model evaluation metrics.
* Serving or downstream delivery requirements.
* Runtime, deployment environment, and operational ownership beyond the three data scientists.
* Retention duration and exact reproducibility guarantees.
