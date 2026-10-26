# How should model versions and scoring inputs be traceable?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to determine which model version and features produced each score. The system therefore needs lifecycle metadata that connects deployed models to their training and data context.

## Decision Drivers

* Auditor traceability
* Model version
* Feature provenance

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

The broader traceability option covers artifacts, runs, metadata, deployment health, and datasets, making it a better fit for auditor review of model and feature provenance. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” support this approach.

### Consequences

* Record model version and feature context for each score.
* Maintain links between deployed artifacts, training runs, and datasets.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts and datasets
* Good, because Tracks runs and deployment health
* Bad, because Requires lifecycle metadata
* Bad, because Adds governance work
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p13`, `s22_p17`

### Artifact version control

* Good, because Versions models and dependencies
* Good, because Supports reproducible deployment
* Bad, because Narrower audit trail
* Bad, because Does not alone link features to scores
