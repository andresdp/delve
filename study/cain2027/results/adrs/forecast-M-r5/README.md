# Architecture decisions: Retail demand forecasting

* [data ingestion mechanism](0001-data-ingestion-mechanism.md)
* [workflow execution coordination](0002-workflow-execution-coordination.md)
* [lifecycle versioning and traceability](0003-lifecycle-versioning-and-traceability.md)
* [candidate model evaluation](0004-candidate-model-evaluation.md)
* [release automation](0005-release-automation.md)
* [prediction delivery mode](0006-prediction-delivery-mode.md)
* [data preservation and provenance](0007-data-preservation-and-provenance.md)
* [development process](0008-development-process.md)

## Not grounded in the design space

* Forecasting-specific model family and seasonal or hierarchical structure.
* Time-aware validation, rolling backtests, forecast horizon, and metric selection.
* Data source contracts, correction handling, and store/product key quality rules.
* Weekly scheduling deadlines, missed-run recovery, and output consumer interface.
