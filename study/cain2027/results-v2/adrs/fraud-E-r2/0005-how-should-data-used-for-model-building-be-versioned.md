# How should data used for model building be versioned?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify which model version and features produced each score; reproducibility also depends on retaining the data basis used to build models. The design space offers dedicated data versioning, repository-based versioning, or no versioning (d:11).

## Decision Drivers

* Audit traceability
* Reproducibility

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Audit traceability decides: an explicit data version gives a model release a reproducible training-data reference. This incurs the cost of a dedicated repository.

### Consequences

* Training data versions must be retained and linked to model releases.
* Storage and version-management costs increase.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: version datasets explicitly
* Good, because Traceability: connect training data to model
* Bad, because Cost: operate a dedicated repository
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Traceability: keep data references near code
* Bad, because Reproducibility: repository fit may constrain data handling
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Reproducibility: training data basis can be lost
* Bad, because Traceability: weak audit trail
* Sources: `d:11`, `v:11.3`
