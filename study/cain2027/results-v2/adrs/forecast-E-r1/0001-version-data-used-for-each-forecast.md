# Version data used for each forecast

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast for any past week requires retaining the data version used to build it (d:11).

## Decision Drivers

* Reproducibility
* Small team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducibility decides the choice: retain explicit data versions so past-week inputs can be recovered, accepting the maintenance cost of a dedicated tool.

### Consequences

* Record the data version associated with each forecast run.
* Maintain the versioned data store and its retention policy.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: dedicated data versioning
* Bad, because Small team: adds a tool to maintain
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Small team: keeps workflow near code
* Bad, because Reproducibility: data handling details unspecified
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Reproducibility: cannot reliably recreate past inputs
* Sources: `d:11`, `v:11.3`
