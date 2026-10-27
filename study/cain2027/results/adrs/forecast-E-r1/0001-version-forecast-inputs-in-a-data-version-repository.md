# Version forecast inputs in a data version repository

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for past weeks, so each run needs a traceable input snapshot. The design space compares repository based versioning with code repository versioning and no versioning.

## Decision Drivers

* Past week reproducibility
* Traceable inputs

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A versioned data snapshot makes past weekly forecasts replayable. The checked design point had no warnings; no sources attested to the combination.

### Consequences

* Record the input snapshot for each forecast run.
* Maintain storage and retention for data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Traceable data snapshots
* Good, because Supports replay
* Bad, because Additional repository workflow
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versioning with code
* Bad, because May complicate large data handling
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Less setup
* Bad, because Past runs harder to reproduce
* Sources: `d:11`, `v:11.3`
