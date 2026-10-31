# Track the full model lifecycle

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labeled images and then pushed to devices. The team needs to relate deployed models to the training process and data that produced them.

## Decision Drivers

* Weekly retraining
* Labeled images
* Device deployment

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Weekly retraining and device pushes make it useful to trace datasets, training runs, artifacts, and deployment health together. “MLOps Principles” describes this integrated lifecycle approach (s22_p03, s22_p04, s22_p06, s22_p08, s22_p17).

### Consequences

* Record dataset and training-run metadata.
* Associate each deployment with a model version.
* The combination checked by `ddspace point` was unattested.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links data and models
* Good, because Tracks runs and health
* Bad, because More metadata to maintain
* Bad, because Needs lifecycle tooling
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p17`

### Artifact version control

* Good, because Versions model assets
* Good, because Supports reproducible reuse
* Bad, because Less lifecycle context
* Bad, because Limited deployment health tracking
* Sources: `s12_p05`, `s19_p05`
