# Architecture decisions: Retail demand forecasting

* [Orchestrated ML pipeline](0001-orchestrated-ml-pipeline.md)
* [Comprehensive ML lifecycle traceability](0002-comprehensive-ml-lifecycle-traceability.md)
* [Scheduled batch prediction deployment](0003-scheduled-batch-prediction-deployment.md)
* [Commit-triggered staged release automation](0004-commit-triggered-staged-release-automation.md)
* [Input and feature-drift monitoring](0005-input-and-feature-drift-monitoring.md)

## Decisions left open

* Data ingestion mechanism and source-of-truth selection; the workflow coordination dimension explicitly requires this decision first.
* Forecast evaluation metrics, acceptance thresholds, and model promotion criteria.
* Historical raw data retention and point-in-time reconstruction policy for each past week.
* Forecast consumer interface, access control, and delivery format.
* Infrastructure and scheduling platform appropriate to the team's operational capacity.
