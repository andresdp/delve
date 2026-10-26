# Data version repository

*How to version data?*

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing forecasts for any past week requires knowing which data produced each result. The brief does not prescribe a versioning mechanism.

## Decision Drivers

* Reproducibility

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides the choice: a dedicated repository makes past input versions identifiable. This adds a separate workflow for a three-person team.

### Consequences

* Record the data version used for each weekly forecast.
* Keep data and code version references together in run records.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: dedicated data versions
* Bad, because Fast iteration: extra repository workflow
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Reproducibility: versions alongside code
* Bad, because Cost: repository may grow with data
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Fast iteration: no versioning setup
* Bad, because Reproducibility: past inputs unclear
* Sources: `d:11`, `v:11.3`
