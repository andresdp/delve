# Use a data version repository to reproduce historical forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, so each run needs a recoverable data version. The design space offers repository-based versioning, code-repository versioning, or no data versioning (d:11).

## Decision Drivers

* Past-week reproducibility
* Traceable inputs

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository best supports retrieving the data used for a given historical forecast. The checked design point had no warnings, though it was unattested in this source-free design space.

### Consequences

* Record the data version with each forecast run.
* Maintain storage and retention for historical data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data versioning
* Good, because Supports input recovery
* Bad, because Adds repository overhead
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versions with code
* Bad, because May complicate large data handling
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Least setup
* Bad, because Cannot reliably reproduce past inputs
* Sources: `d:11`, `v:11.3`
