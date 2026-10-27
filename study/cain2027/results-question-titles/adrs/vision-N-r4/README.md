# Architecture decisions: On-device visual inspection

* [On-device inference](0001-on-device-inference.md)
* [Device-initiated download](0002-device-initiated-download.md)
* [Stage, validate, and retain prior model](0003-stage-validate-and-retain-prior-model.md)
* [Central training pipeline](0004-central-training-pipeline.md)
* [Versioned, immutable model packages](0005-versioned-immutable-model-packages.md)

## Decisions left open

* Camera hardware, operating system, and supported inference runtime.
* Model architecture, accuracy targets, and acceptance criteria.
* How labelled images are collected, transferred, stored, and governed.
* Update authentication, integrity checks, and authorization.
* Fleet size, rollout rings, monitoring, and update success criteria.
* Training compute, package hosting, and infrastructure budget limits.
