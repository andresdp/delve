# Architecture decisions: Retail demand forecasting

* [forecast workflow coordination](0001-forecast-workflow-coordination.md)
* [model and data lineage](0002-model-and-data-lineage.md)
* [input data preservation](0003-input-data-preservation.md)
* [candidate model validation](0004-candidate-model-validation.md)
* [pipeline integration checks](0005-pipeline-integration-checks.md)
* [forecast computation and delivery](0006-forecast-computation-and-delivery.md)
* [model development process](0007-model-development-process.md)

## Not grounded in the design space

* Forecast model family and forecasting objective, including seasonality and store/product hierarchy.
* Exact weekly schedule, data arrival cutoff, and recovery procedure for a missed run.
* Evaluation metrics, acceptance thresholds, and business impact measures for retail demand.
* Data-source ingestion mechanism and handling of late or corrected sales data.
* Compute infrastructure, storage technology, retention duration, and access policy.
