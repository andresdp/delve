# Versioning data used for model work

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify the model and features behind a score; reproducibility also depends on knowing which data informed model development.

## Decision Drivers

* Reproducibility
* Audit trail
* Model release traceability

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository makes it possible to link a model release to the data version used during development. That strengthens reproducibility alongside per-score model and feature records.

### Consequences

* Store the training data version with each model release.
* Maintain access to referenced data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data versioning support
* Good, because Reproducible data references
* Bad, because Extra repository operations
* Bad, because Data references need management
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Co-located with code history
* Good, because Familiar workflow
* Bad, because May constrain data size
* Bad, because Data and code release coupling
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No versioning system to operate
* Good, because Simple initial workflow
* Bad, because Harder to reproduce training
* Bad, because Weak audit trail
* Sources: `d:11`, `v:11.3`
