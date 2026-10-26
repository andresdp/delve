# Architecture decisions: On-device visual inspection

* [how should predictions run on production cameras](0001-how-should-predictions-run-on-production-cameras.md)
* [how should the application integrate the model](0002-how-should-the-application-integrate-the-model.md)
* [when and how should models be trained](0003-when-and-how-should-models-be-trained.md)
* [how should training data be versioned](0004-how-should-training-data-be-versioned.md)
* [how should weekly integration and delivery be automated](0005-how-should-weekly-integration-and-delivery-be-automated.md)
* [what should trigger retraining](0006-what-should-trigger-retraining.md)
* [how should a deployed model be rolled back](0007-how-should-a-deployed-model-be-rolled-back.md)
* [how should training and labelled images be stored](0008-how-should-training-and-labelled-images-be-stored.md)
* [how should model quality be monitored in production](0009-how-should-model-quality-be-monitored-in-production.md)

## Not grounded in the design space

* How devices receive model packages while offline, including connectivity windows, transfer security, and rollout coordination.
* Device hardware, model runtime, latency target, and local resource limits.
* What prediction-quality metrics and acceptance thresholds gate a release.
* How devices record and later transfer inspection data and monitoring results.
* How training data is labelled, stored, and synchronized from production sites.
