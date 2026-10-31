# Architecture decisions: Retail demand forecasting

* [Forecast weekly demand per store and product](0001-forecast-weekly-demand-per-store-and-product.md)
* [Make past-week forecasts reproducible from versioned inputs and code](0002-make-past-week-forecasts-reproducible-from-versioned-inputs-.md)
* [Validate candidate models before production promotion](0003-validate-candidate-models-before-production-promotion.md)
* [Have the three-person data science team own the pipeline end to end](0004-have-the-three-person-data-science-team-own-the-pipeline-end.md)

## Decisions left open

* Source systems, input schemas, and data quality rules
* Forecast horizon and whether forecasts are updated within the week
* Model family, feature design, and retraining schedule
* Evaluation metrics and candidate promotion thresholds
* Weekly run schedule, orchestration platform, and failure recovery
* Production runtime, forecast consumers, and output interface
* Artifact storage, versioning mechanism, and retention period
* Monitoring, alerting, access controls, and privacy requirements
