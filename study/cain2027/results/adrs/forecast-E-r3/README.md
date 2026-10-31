# Architecture decisions: Retail demand forecasting

* [Version forecasting data in a dedicated repository](0001-version-forecasting-data-in-a-dedicated-repository.md)
* [Process weekly demand data in batches](0002-process-weekly-demand-data-in-batches.md)
* [Automate data preparation in a pipeline](0003-automate-data-preparation-in-a-pipeline.md)
* [Build and evaluate models in an automated pipeline](0004-build-and-evaluate-models-in-an-automated-pipeline.md)
* [Use batch-based model learning](0005-use-batch-based-model-learning.md)
* [Use CI/CD to deliver pipeline changes](0006-use-ci-cd-to-deliver-pipeline-changes.md)

## Decisions left open

* How forecasts are served to users or downstream systems, including batch file delivery versus an API.
* How candidate models are compared and approved, including demand-forecast error measures and acceptance thresholds.
* How production forecasts and model performance are monitored, and what actions follow a regression.
* How historical forecast runs are reconstructed end to end, including code, configuration, dependencies, and model artifact retention.
* How weekly runs are scheduled, retried, and handled when input data is late or incomplete.
* How to isolate experiments from the production weekly run and release model candidates safely.
