# Architecture decisions: Retail demand forecasting

* [Batch-based data processing](0001-batch-based-data-processing.md)
* [Data version repository](0002-data-version-repository.md)
* [On-schedule trigger](0003-on-schedule-trigger.md)
* [Model building pipeline](0004-model-building-pipeline.md)
* [CI/CD pipeline](0005-ci-cd-pipeline.md)
* [Build, test, and deploy machine learning pipelines and components needed during pipeline runs](0006-build-test-and-deploy-machine-learning-pipelines-and-compone.md)
* [Testing trained model quality](0007-testing-trained-model-quality.md)
* [Model performance monitoring](0008-model-performance-monitoring.md)

## Decisions left open

* How to define forecast quality metrics and acceptance thresholds.
* How to capture and retain each run's code, configuration, and model artifacts for full past-week reproduction.
* How to promote and roll back a model while preserving the weekly production run.
* How to manage late or corrected data for a completed forecast week.
