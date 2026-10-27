# Architecture decisions: On-device visual inspection

* [how should the model serve predictions](0001-how-should-the-model-serve-predictions.md)
* [when and how should the model be trained](0002-when-and-how-should-the-model-be-trained.md)
* [how should training data be versioned](0003-how-should-training-data-be-versioned.md)
* [how should model integration and delivery be automated](0004-how-should-model-integration-and-delivery-be-automated.md)
* [how should deployed model versions be handled](0005-how-should-deployed-model-versions-be-handled.md)
* [how should model performance be monitored](0006-how-should-model-performance-be-monitored.md)

## Not grounded in the design space

* How to distribute model packages to intermittently connected devices and manage deferred updates.
* How to collect labels and images from devices when network access is unavailable.
* What device-side hardware, model format, and resource limits to target.
* How to test model quality against defect-specific acceptance thresholds.
