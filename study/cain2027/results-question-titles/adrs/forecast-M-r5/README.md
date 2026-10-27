# Architecture decisions: Retail demand forecasting

* [Data ingestion mechanism](0001-data-ingestion-mechanism.md)
* [Workflow execution coordination](0002-workflow-execution-coordination.md)
* [Lifecycle versioning and traceability](0003-lifecycle-versioning-and-traceability.md)
* [Candidate model evaluation](0004-candidate-model-evaluation.md)
* [Release automation](0005-release-automation.md)
* [Prediction delivery mode](0006-prediction-delivery-mode.md)
* [Data preservation and provenance](0007-data-preservation-and-provenance.md)
* [Development process](0008-development-process.md)

## Decisions left open

* Forecasting-specific model family and seasonal or hierarchical structure.
* Time-aware validation, rolling backtests, forecast horizon, and metric selection.
* Data source contracts, correction handling, and store/product key quality rules.
* Weekly scheduling deadlines, missed-run recovery, and output consumer interface.
