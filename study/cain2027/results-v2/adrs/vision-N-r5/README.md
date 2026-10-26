# Architecture decisions: On-device visual inspection

* [run inference on device](0001-run-inference-on-device.md)
* [package each model as a versioned release](0002-package-each-model-as-a-versioned-release.md)
* [distribute releases through an update service with device si](0003-distribute-releases-through-an-update-service-with-device-si.md)
* [retain labelled images and training inputs as a reproducible](0004-retain-labelled-images-and-training-inputs-as-a-reproducible.md)

## Not grounded in the design space

* How devices authenticate updates and verify artifact integrity.
* How to roll back a model that causes degraded inspection results.
* How devices report model health and inspection outcomes when connectivity returns.
* Dataset retention duration and handling of sensitive image data.
