# How should historical data be versioned?

* System: Retail demand forecasting

## Context and Problem Statement

The team must be able to reproduce a forecast for any past week, which requires identifying the input data used for each run.

## Decision Drivers

* Past-week reproducibility
* Three-person team

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated data version repository directly supports selecting the exact historical inputs for a past forecast; the checked combination had no warnings and no attested sources.

### Consequences

* Each forecast run must record its data version.
* The team maintains a data versioning workflow.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data version support
* Good, because Makes past inputs identifiable
* Bad, because Adds repository workflow
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps changes near code
* Bad, because May complicate large data versioning
* Sources: `d:11`, `v:11.2`

### No data versioning

* Bad, because Cannot reliably reproduce past inputs
* Sources: `d:11`, `v:11.3`
