# How should training and model artifacts be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Models are retrained weekly from newly labelled images, so the team needs to relate a deployed model to its training run and data. Lifecycle traceability supports that reproducibility need.

## Decision Drivers

* Reproducibility
* Weekly updates
* Small team

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Reproducibility decides the choice: link training data, runs, artifacts, and deployment state to explain each weekly model. This costs the small team additional metadata and governance work.

### Consequences

* Record dataset versions and training context with each model.
* Track deployed model versions and their operational health.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Reproducibility: links data, runs, and deployed models
* Good, because Weekly updates: tracks deployment health
* Bad, because Small team: integrated governance adds overhead
* Bad, because Weekly updates: more metadata to maintain
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p13`, `s22_p17`

### Artifact version control

* Good, because Small team: simpler versioning scope
* Good, because Weekly updates: identifies model artifacts
* Bad, because Reproducibility: limited lineage to data and runs
* Bad, because Weekly updates: deployment health is not covered
* Sources: `s12_p05`, `s19_p05`
