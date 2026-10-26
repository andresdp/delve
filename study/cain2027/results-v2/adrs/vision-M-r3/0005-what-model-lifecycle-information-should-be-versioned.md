# What model lifecycle information should be versioned?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining and device deployment require identifying which model is running and how it was produced. The design space offers broad lifecycle traceability as well as artifact-only version control.

## Decision Drivers

* Reproducibility
* Small team
* Weekly update cadence

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Reproducibility decides the choice: linking datasets, runs, artifacts, and deployment health supports tracing weekly model changes. This gives up the lower upkeep of artifact-only versioning.

### Consequences

* Record training data and run metadata with each model.
* Track the model version installed on each device.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Reproducibility: links data, runs, and models
* Good, because Weekly cadence: records deployment health
* Bad, because Small team: broader metadata upkeep
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`

### Artifact version control

* Good, because Small team: tracks deployable model artifacts
* Good, because Weekly cadence: supports known versions
* Bad, because Reproducibility: omits full training context
