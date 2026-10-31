# Data version repository

*How should past input data be versioned?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, which requires retaining the input data state used by each run.

## Decision Drivers

* Past-week reproducibility
* Traceable inputs

## Considered Options

* Data version repository (`v:11.1`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository provides a way to retain and retrieve the inputs for past forecast runs (d:11, v:11.1).

### Consequences

* Each run must record its data version.
* Historical data versions require storage and maintenance.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data versioning
* Good, because Supports historical inputs
* Bad, because Requires repository upkeep
* Sources: `d:11`, `v:11.1`

### No data versioning

* Good, because No versioning overhead
* Bad, because Past runs may be unreproducible
* Sources: `d:11`, `v:11.3`
