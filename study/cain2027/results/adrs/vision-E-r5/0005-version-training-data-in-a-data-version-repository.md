# Version training data in a data version repository

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images feed weekly retraining. Versioning the data helps connect a released model to the training inputs used to build it.

## Decision Drivers

* weekly retraining
* traceability

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Versioned training inputs make weekly model releases easier to trace and reproduce, which supports safe delivery and rollback.

### Consequences

* Store references to data versions with each model release.
* Budget for data storage and repository upkeep.

## Pros and Cons of the Options

### Data version repository

* Good, because explicit data versions
* Good, because reproducible training inputs
* Bad, because repository overhead
* Bad, because storage needs
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because less tooling
* Good, because lower setup effort
* Bad, because harder to reproduce training
* Bad, because weak traceability
* Sources: `d:11`, `v:11.3`
