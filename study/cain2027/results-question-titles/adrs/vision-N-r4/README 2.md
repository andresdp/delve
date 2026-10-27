# Architecture decisions: On-device visual inspection

* [where should defect inference run](0001-where-should-defect-inference-run.md)
* [how should weekly model updates reach devices](0002-how-should-weekly-model-updates-reach-devices.md)
* [how should model updates be activated](0003-how-should-model-updates-be-activated.md)
* [where should model training run](0004-where-should-model-training-run.md)
* [how should model packages be versioned](0005-how-should-model-packages-be-versioned.md)

## Not grounded in the design space

* Camera hardware, operating system, and supported inference runtime.
* Model architecture, accuracy targets, and acceptance criteria.
* How labelled images are collected, transferred, stored, and governed.
* Update authentication, integrity checks, and authorization.
* Fleet size, rollout rings, monitoring, and update success criteria.
* Training compute, package hosting, and infrastructure budget limits.
