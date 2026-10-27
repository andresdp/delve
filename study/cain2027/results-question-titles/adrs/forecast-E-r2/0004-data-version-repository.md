# Data version repository

*How should training data be versioned?*

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing forecasts for any past week requires identifying the data used in that run. The design space includes a dedicated data version repository. [d:11, v:11.1]

## Decision Drivers

* Historical reproducibility
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

An explicit data version repository gives each historical run a stable data reference, which is central to the reproducibility requirement. [d:11, v:11.1]

### Consequences

* Retain data versions for the required history.
* Record the selected data version with each forecast run.

## Pros and Cons of the Options

### Data version repository

* Good, because Explicit data versions
* Good, because Supports reruns
* Bad, because Repository upkeep
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versions near code
* Bad, because Data may strain code repository
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Cannot reliably reconstruct past inputs
* Sources: `d:11`, `v:11.3`
