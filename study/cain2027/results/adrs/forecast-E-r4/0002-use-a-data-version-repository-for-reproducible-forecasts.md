# Use a data version repository for reproducible forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast for any past week requires identifying the data used for that run. The design space includes a dedicated data version repository and versioning in a code repository (d:11).

## Decision Drivers

* Past-week reproducibility
* Traceable inputs

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A data version repository directly supports identifying the historical input data for a forecast rerun (d:11, v:11.1).

### Consequences

* Retain dataset versions used by production runs.
* Track each run against its input version.

## Pros and Cons of the Options

### Data version repository

* Good, because Versions datasets
* Bad, because Adds repository upkeep
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versioning with code
* Bad, because May not suit dataset scale
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No versioning overhead
* Bad, because Weak past-run reproducibility
* Sources: `d:11`, `v:11.3`
