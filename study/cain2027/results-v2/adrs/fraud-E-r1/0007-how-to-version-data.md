# How to version data?

* System: Card-fraud scoring service

## Context and Problem Statement

Reproducing an audited score depends on identifying the data and features used during model development and production (d:11).

## Decision Drivers

* Reproducibility
* Audit traceability

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides the choice: explicit data versions support repeatable model builds; operating a separate repository adds management cost.

### Consequences

* Keep data versions linked to model releases.
* Retain the feature inputs or references needed to reconstruct a score.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: explicit data versions
* Bad, because Audit traceability: repository requires management
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Reproducibility: versioned with code
* Bad, because Audit traceability: large data handling may be constrained
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Reproducibility: inputs may not be recoverable
* Sources: `d:11`, `v:11.3`
