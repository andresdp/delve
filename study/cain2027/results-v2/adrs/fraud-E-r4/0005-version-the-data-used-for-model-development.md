# Version the data used for model development

* System: Card-fraud scoring service

## Context and Problem Statement

The audit requirement names production features, while reproducibility of model training data is not specified. Data versioning is available as a related design choice (d:11).

## Decision Drivers

* Audit traceability

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Audit traceability favors explicitly versioned data; the brief does not require training-data reproducibility, so this choice supports broader model lineage at added repository cost.

### Consequences

* Training runs must reference data versions.
* The brief’s per-score audit record still needs production feature values or immutable references.

## Pros and Cons of the Options

### Data version repository

* Good, because Audit traceability: identifies data snapshots
* Bad, because Audit traceability: adds repository management
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Audit traceability: keeps data references with code
* Bad, because Audit traceability: large data may complicate repository use
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Audit traceability: weak training-data reproducibility
* Sources: `d:11`, `v:11.3`
