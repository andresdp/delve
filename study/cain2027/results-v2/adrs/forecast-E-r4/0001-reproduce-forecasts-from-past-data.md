# Reproduce forecasts from past data

* System: Retail demand forecasting

## Context and Problem Statement

The system must recreate forecasts for any past week. The brief does not specify a storage mechanism, so this ADR uses data versioning as the grounded design choice.

## Decision Drivers

* 1. Past-week reproducibility
* 2. Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Past-week reproducibility decides the choice: explicitly versioning data supports reconstruction. The cost is added repository management for a three-person team.

### Consequences

* Record the data version used for each weekly forecast.
* The design space has no sources or attested systems for this choice.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: versions data explicitly
* Bad, because Small team: adds a repository to manage
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Small team: keeps data versioning near code
* Bad, because Reproducibility: may not suit large data
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Reproducibility: cannot reliably recreate past inputs
* Sources: `d:11`, `v:11.3`
