# Architecture decisions: Retail demand forecasting

* [how should weekly demand data be processed](0001-how-should-weekly-demand-data-be-processed.md)
* [how should model building and training run](0002-how-should-model-building-and-training-run.md)
* [how should training be scheduled](0003-how-should-training-be-scheduled.md)
* [how should training data be versioned](0004-how-should-training-data-be-versioned.md)
* [how should the forecast pipeline be triggered](0005-how-should-the-forecast-pipeline-be-triggered.md)
* [what should ci cd build and deploy](0006-what-should-ci-cd-build-and-deploy.md)
* [how should a production model be replaced safely](0007-how-should-a-production-model-be-replaced-safely.md)
* [how should production model performance be monitored](0008-how-should-production-model-performance-be-monitored.md)

## Not grounded in the design space

* Forecast error metrics, acceptance thresholds, and promotion gates.
* Forecast storage, delivery, and consumer interface.
* Retention period and exact mechanism for historical input snapshots.
