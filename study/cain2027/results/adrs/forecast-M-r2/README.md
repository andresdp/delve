# Architecture decisions: Retail demand forecasting

* [Version pipelines, data, and model artifacts together](0001-version-pipelines-data-and-model-artifacts-together.md)
* [Orchestrate recurring training and evaluation as an ML pipeline](0002-orchestrate-recurring-training-and-evaluation-as-an-ml-pipel.md)
* [Release model updates progressively with rollback](0003-release-model-updates-progressively-with-rollback.md)
* [Evaluate candidates offline before promotion](0004-evaluate-candidates-offline-before-promotion.md)

## Decisions left open

* Data ingestion mechanism and source-data snapshot policy are not determined by the brief or grounded by the checked alternatives; both affect reproducibility of past-week forecasts.
* Forecast-specific error metrics, acceptance thresholds, and business-impact evaluation criteria are unspecified.
