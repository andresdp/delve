# Track model, feature, and dataset lineage across the lifecycle

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to determine which model version and features produced a score. Lifecycle traceability links models and datasets to their training and deployment context.

## Decision Drivers

* Audit reconstruction
* Model version

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Choose lifecycle traceability because artifact version alone does not establish the feature and dataset context needed to reconstruct a score. “MLOps Principles” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support integrated lineage. The checked design point had no warnings but was unattested.

### Consequences

* Persist model version and feature provenance with each score.
* Retain lifecycle metadata for the required audit period.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts and datasets
* Good, because Includes deployment health
* Bad, because Requires consistent metadata capture
* Sources: `s08_p01`, `s22_p03`, `s22_p06`

### Artifact version control

* Good, because Versions model artifacts
* Good, because Simpler scope
* Bad, because Limited lineage context
* Sources: `s22_p03`, `s22_p04`
