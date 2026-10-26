# Architecture decisions: On-device visual inspection

* [how should inference run on production cameras](0001-how-should-inference-run-on-production-cameras.md)
* [how should predictions be served](0002-how-should-predictions-be-served.md)
* [how should weekly retraining run](0003-how-should-weekly-retraining-run.md)
* [how should training data be versioned](0004-how-should-training-data-be-versioned.md)
* [how should model delivery be automated](0005-how-should-model-delivery-be-automated.md)
* [how should production model versions be managed](0006-how-should-production-model-versions-be-managed.md)
* [what should be monitored in production](0007-what-should-be-monitored-in-production.md)

## Not grounded in the design space

* Offline device update protocol, including package transfer, retries, and fleet rollout strategy.
* Camera hardware sizing, inference latency targets, and resource limits.
* Model acceptance thresholds, defect class metrics, and labeling quality controls.
* Security, authentication, and integrity checks for model artifacts and device updates.
* Retention and privacy rules for production images, predictions, and logs.
