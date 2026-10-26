# How should historical data be versioned?

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast for any past week requires identifying the data used for that run. The design space includes a dedicated data version repository and other versioning options.

## Decision Drivers

* Past-week reproducibility
* End-to-end ownership

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository directly supports identifying historical inputs. The checked design point has no warnings; no sources attest to the combination.

### Consequences

* Associate each forecast run with a data version.
* Maintain the data versions needed for historical reruns.

## Pros and Cons of the Options

### Data version repository

* Good, because Tracks data versions
* Bad, because Requires repository upkeep
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versions with code
* Bad, because Data may not fit code repository
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No versioning overhead
* Bad, because Weak reproducibility
* Sources: `d:11`, `v:11.3`
