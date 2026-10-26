# Architecture decisions: Retail demand forecasting

* [how should weekly inputs be processed](0001-how-should-weekly-inputs-be-processed.md)
* [how should historical data be versioned](0002-how-should-historical-data-be-versioned.md)
* [what should trigger the forecasting pipeline](0003-what-should-trigger-the-forecasting-pipeline.md)
* [how should models be built and validated](0004-how-should-models-be-built-and-validated.md)
* [how should changes reach production](0005-how-should-changes-reach-production.md)
* [what should automated delivery build and deploy](0006-what-should-automated-delivery-build-and-deploy.md)
* [what should be tested before a model is used](0007-what-should-be-tested-before-a-model-is-used.md)
* [how should production model performance be monitored](0008-how-should-production-model-performance-be-monitored.md)

## Not grounded in the design space

* How to define forecast quality metrics and acceptance thresholds.
* How to capture and retain each run's code, configuration, and model artifacts for full past-week reproduction.
* How to promote and roll back a model while preserving the weekly production run.
* How to manage late or corrected data for a completed forecast week.
