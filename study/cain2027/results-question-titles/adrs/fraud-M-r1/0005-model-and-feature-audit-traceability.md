# Model and feature audit traceability

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify the model version and features behind each score. The brief makes that record a system requirement.

## Decision Drivers

* Auditor traceability
* Model version per score
* Features per score

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Comprehensive lifecycle traceability covers artifacts and metadata, while the brief specifically requires a per-score record of model version and features. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” support the broader traceability approach.

### Consequences

* Persist model version and feature references with each score.
* Retain records in a form auditors can retrieve.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts, runs, datasets, and metadata
* Good, because Supports lifecycle audit trail
* Bad, because More metadata to manage
* Bad, because Needs consistent capture at serving time
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p13`, `s22_p17`

### Artifact version control

* Good, because Tracks model artifacts and dependencies
* Good, because Supports reproducible deployment
* Bad, because Does not alone link each score to its features
* Bad, because Narrower lifecycle record
