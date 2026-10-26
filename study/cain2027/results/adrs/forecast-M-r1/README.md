# Architecture decisions: Retail demand forecasting

* [reproducibility and lifecycle traceability](0001-reproducibility-and-lifecycle-traceability.md)
* [weekly workflow coordination](0002-weekly-workflow-coordination.md)
* [model release safety](0003-model-release-safety.md)
* [pre release forecast evaluation](0004-pre-release-forecast-evaluation.md)
* [data preservation for forecast replay](0005-data-preservation-for-forecast-replay.md)

## Not grounded in the design space

* Data-ingestion mechanism and source-system interfaces; the checked design point says workflow coordination requires this decision first.
* Forecasting model family and business-selected error metric or acceptance thresholds.
* Weekly schedule, late-data handling, and rerun policy.
* Data-retention duration, access controls, and privacy constraints.
* Production monitoring signals and alert ownership.
