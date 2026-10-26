# Architecture decisions: Retail demand forecasting

* [Scheduled batch pipeline](0001-scheduled-batch-pipeline.md)
* [Modular pipeline in one codebase](0002-modular-pipeline-in-one-codebase.md)
* [Versioned inputs, code, and run metadata](0003-versioned-inputs-code-and-run-metadata.md)
* [Isolated experiments with explicit promotion](0004-isolated-experiments-with-explicit-promotion.md)

## Decisions left open

* Demand data sources, schemas, and availability guarantees
* Forecast horizon and required accuracy measures
* Model selection, training cadence, and fallback behavior
* Execution platform, orchestration tooling, and deployment environment
* Access controls, privacy requirements, and data retention period
* Monitoring, alerting, and recovery expectations
* Forecast consumers, output format, and delivery interface
* Promotion criteria and approval process
