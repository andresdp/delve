# How should data be versioned for reproducibility?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to know which features produced a score; reconstructing those features requires retaining their identity or values.

## Decision Drivers

* Feature traceability
* Reproducibility

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides: a dedicated repository can identify data versions used for model work and support traceability. We accept operating the extra repository; transaction level feature capture still needs to be defined.

### Consequences

* Retain a version reference or feature snapshot with each score.
* Define retention and access rules for sensitive transaction features.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: dedicated data version history
* Bad, because Feature traceability: extra repository to operate
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Reproducibility: versioned alongside code
* Bad, because Feature traceability: less suited to changing transaction data
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Reproducibility: inputs cannot be reconstructed
* Sources: `d:11`, `v:11.3`
