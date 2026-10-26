# Architecture decisions: Retail demand forecasting

* [Forecast workflow coordination](0001-forecast-workflow-coordination.md)
* [Model and data lineage](0002-model-and-data-lineage.md)
* [Input data preservation](0003-input-data-preservation.md)
* [Candidate model validation](0004-candidate-model-validation.md)
* [Pipeline integration checks](0005-pipeline-integration-checks.md)
* [Forecast computation and delivery](0006-forecast-computation-and-delivery.md)
* [Model development process](0007-model-development-process.md)

## Decisions left open

* Forecast model family and forecasting objective, including seasonality and store/product hierarchy.
* Exact weekly schedule, data arrival cutoff, and recovery procedure for a missed run.
* Evaluation metrics, acceptance thresholds, and business impact measures for retail demand.
* Data-source ingestion mechanism and handling of late or corrected sales data.
* Compute infrastructure, storage technology, retention duration, and access policy.
