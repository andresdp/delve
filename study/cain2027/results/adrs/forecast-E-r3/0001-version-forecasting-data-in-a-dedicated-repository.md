# Version forecasting data in a dedicated repository

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, so the training data used for each run needs a versioned reference. The design space compares dedicated data versioning with storing versioning alongside code and no data versioning (d:11).

## Decision Drivers

* Past-week reproducibility
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository directly supports recovering the inputs for historical weekly runs (d:11, v:11.1). The design-point check returned no warnings, but no attesting sources; the combination is novel in this workspace.

### Consequences

* Record the data version with each forecast run.
* Maintain and operate data versioning alongside code.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data history
* Good, because Supports repeatable inputs
* Bad, because Additional repository workflow
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Co-locates code and data references
* Bad, because May couple data workflow to code
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Least setup
* Bad, because Past runs hard to reproduce
* Sources: `d:11`, `v:11.3`
