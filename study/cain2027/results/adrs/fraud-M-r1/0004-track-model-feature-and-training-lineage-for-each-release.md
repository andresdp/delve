# Track model, feature, and training lineage for each release

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to determine which model version and features produced a score; the brief requires traceability but gives no specific record format.

## Decision Drivers

* Audit traceability
* Model version identification
* Feature provenance

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Integrated lifecycle metadata best supports identifying deployed model versions and their training context. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” describe traceability across artifacts, datasets, runs, and deployments.

### Consequences

* Serving records need links to model and feature versions.
* Metadata capture and retention add storage and operational work.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts and datasets
* Good, because Includes deployment metadata
* Bad, because Requires lifecycle metadata discipline
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`

### Artifact version control

* Good, because Versions model artifacts
* Bad, because Limited training and data lineage
* Sources: `s22_p03`
