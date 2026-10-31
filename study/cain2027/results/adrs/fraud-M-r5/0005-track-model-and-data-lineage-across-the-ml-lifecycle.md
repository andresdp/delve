# Track model and data lineage across the ML lifecycle

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify the model version and features behind each score. Lifecycle metadata and dataset lineage provide a basis for that traceability.

## Decision Drivers

* Auditor traceability
* Model version identification

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Comprehensive traceability best supports later audit of deployed model versions and their data context. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” describe integrated lifecycle records; the brief’s per-score audit detail still needs a concrete record format and retention policy.

### Consequences

* Record deployed model identifiers and feature provenance.
* Lifecycle metadata must remain available for audit.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links models and datasets
* Good, because Tracks lifecycle metadata
* Bad, because Requires metadata discipline
* Bad, because Does not specify per-score retention
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`

### Artifact version control

* Good, because Versions model artifacts
* Good, because Supports reproducible deployment
* Bad, because Narrower lifecycle coverage
* Bad, because Does not link each score to features
* Sources: `s12_p05`, `s19_p05`
