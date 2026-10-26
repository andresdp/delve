# How should historical inputs be reproduced?

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, which requires identifying the data used for each run.

## Decision Drivers

* Historical reproducibility
* Weekly pipeline
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository makes it possible to associate historical forecasts with their inputs (d:11, v:11.1).

### Consequences

* Each run records its data version.
* Storage and retention need management.

## Pros and Cons of the Options

### Data version repository

* Good, because Tracks data versions
* Good, because Supports reruns
* Bad, because Requires repository upkeep
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps records near code
* Bad, because Data scale may not fit
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Less setup
* Bad, because Past runs hard to reproduce
* Sources: `d:11`, `v:11.3`
