# Architecture decisions: Retail demand forecasting

* [Separate training and forecast pipelines](0001-separate-training-and-forecast-pipelines.md)
* [Version data, code, configuration, and model artifacts per run](0002-version-data-code-configuration-and-model-artifacts-per-run.md)
* [Promote models through validation and staged release](0003-promote-models-through-validation-and-staged-release.md)

## Decisions left open

* Forecast accuracy targets and evaluation metrics
* Data sources, freshness, and quality requirements
* Weekly run deadline and recovery expectations
* Forecast serving or delivery interface
* Compute, storage, and deployment constraints
