# Architecture decisions: Retail demand forecasting

* [how should source data be ingested](0001-how-should-source-data-be-ingested.md)
* [how should data be processed](0002-how-should-data-be-processed.md)
* [how should past input data be versioned](0003-how-should-past-input-data-be-versioned.md)
* [how should the pipeline be triggered](0004-how-should-the-pipeline-be-triggered.md)
* [how should model building be organized](0005-how-should-model-building-be-organized.md)
* [when should models be trained](0006-when-should-models-be-trained.md)
* [how should integration and delivery be automated](0007-how-should-integration-and-delivery-be-automated.md)
* [what should automated delivery build and deploy](0008-what-should-automated-delivery-build-and-deploy.md)
* [what should be monitored in production](0009-what-should-be-monitored-in-production.md)
* [what should the pipeline test](0010-what-should-the-pipeline-test.md)

## Not grounded in the design space

* Forecasting model family and feature design.
* Forecast quality metric and acceptance thresholds.
* Prediction serving interface and forecast consumers.
* Retention policy and storage location for versioned data and model artifacts.
* Rollback and recovery procedure for a failed weekly run.
