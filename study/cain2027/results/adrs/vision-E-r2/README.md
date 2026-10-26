# Architecture decisions: On-device visual inspection

* [how is the model integrated](0001-how-is-the-model-integrated.md)
* [how are predictions served](0002-how-are-predictions-served.md)
* [when and how is the model trained](0003-when-and-how-is-the-model-trained.md)
* [what triggers the training pipeline](0004-what-triggers-the-training-pipeline.md)
* [how is model delivery automated](0005-how-is-model-delivery-automated.md)
* [how are production model versions managed](0006-how-are-production-model-versions-managed.md)
* [what is monitored in production](0007-what-is-monitored-in-production.md)

## Not grounded in the design space

* Device update transport, fleet targeting, and offline package synchronization.
* Camera hardware sizing, model runtime, and inference latency targets.
* Image labelling workflow, dataset governance, and label quality controls.
* Model acceptance thresholds and production release gates.
* Security, access control, and protection of stored images and logs.
