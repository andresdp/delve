# Architecture decisions: Retail demand forecasting

* [prioritize requirements](0001-prioritize-requirements.md)
* [how to version training data](0002-how-to-version-training-data.md)
* [when and how to train](0003-when-and-how-to-train.md)
* [how to trigger the ml pipeline](0004-how-to-trigger-the-ml-pipeline.md)
* [how to automate integration and delivery](0005-how-to-automate-integration-and-delivery.md)
* [how to test pipeline changes](0006-how-to-test-pipeline-changes.md)
* [how to deploy and recover model versions](0007-how-to-deploy-and-recover-model-versions.md)

## Not grounded in the design space

* Forecast serving interface and consumers
* Storage format and retention for historical forecasts
* Forecast accuracy metric and acceptance threshold
* Experiment isolation and promotion workflow
* Monitoring, alerting, and ownership for failed weekly runs
* Compute budget and runtime limits
