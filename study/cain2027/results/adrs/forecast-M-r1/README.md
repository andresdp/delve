# Architecture decisions: Retail demand forecasting

* [Use an orchestrated ML pipeline](0001-use-an-orchestrated-ml-pipeline.md)
* [Track the full ML lifecycle for reproducibility](0002-track-the-full-ml-lifecycle-for-reproducibility.md)
* [Use commit-triggered staged release automation](0003-use-commit-triggered-staged-release-automation.md)
* [Evaluate candidates offline before promotion](0004-evaluate-candidates-offline-before-promotion.md)
* [Monitor input and feature drift in production](0005-monitor-input-and-feature-drift-in-production.md)

## Decisions left open

* Data ingestion mechanism and source-system integration; the checked design point indicates workflow coordination requires this decision.
* Forecasting model family and model update policy.
* Prediction serving mode, forecast delivery interface, and fallback behavior for a failed weekly run.
* Forecast-specific metrics, acceptance thresholds, and rollback criteria.
