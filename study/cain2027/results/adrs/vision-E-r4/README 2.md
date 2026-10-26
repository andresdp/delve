# Architecture decisions: On-device visual inspection

* [how should inference run on each camera](0001-how-should-inference-run-on-each-camera.md)
* [how should the application serve predictions](0002-how-should-the-application-serve-predictions.md)
* [how should training be triggered and performed](0003-how-should-training-be-triggered-and-performed.md)
* [how should model delivery be automated](0004-how-should-model-delivery-be-automated.md)
* [how should rollout failures be handled](0005-how-should-rollout-failures-be-handled.md)
* [how should training data be versioned](0006-how-should-training-data-be-versioned.md)
* [what should be tested before model rollout](0007-what-should-be-tested-before-model-rollout.md)
* [how should production behavior be tracked](0008-how-should-production-behavior-be-tracked.md)

## Not grounded in the design space

* Device communication and artifact synchronization during intermittent connectivity.
* Model artifact security, integrity, and device authentication.
* Image retention and privacy requirements.
* Evaluation metric and minimum acceptable defect-detection quality.
