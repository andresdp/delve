# Architecture decisions: Retail demand forecasting

* [Reproducibility and lifecycle traceability](0001-reproducibility-and-lifecycle-traceability.md)
* [Weekly workflow coordination](0002-weekly-workflow-coordination.md)
* [Model release safety](0003-model-release-safety.md)
* [Pre-release forecast evaluation](0004-pre-release-forecast-evaluation.md)
* [Data preservation for forecast replay](0005-data-preservation-for-forecast-replay.md)

## Decisions left open

* Data-ingestion mechanism and source-system interfaces; the checked design point says workflow coordination requires this decision first.
* Forecasting model family and business-selected error metric or acceptance thresholds.
* Weekly schedule, late-data handling, and rerun policy.
* Data-retention duration, access controls, and privacy constraints.
* Production monitoring signals and alert ownership.
