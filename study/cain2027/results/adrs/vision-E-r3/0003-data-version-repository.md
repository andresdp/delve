# Data version repository

*How to version training data?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images feed each weekly model build, so the team needs to relate a trained model to its input data. The design space identifies alternatives but provides no source evidence.

## Decision Drivers

* Weekly data updates
* Traceability
* Tight budget

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A dedicated repository links weekly training inputs to model builds; the brief's labelled images make reproducibility useful. The design point has no warnings, but no attesting sources.

### Consequences

* Budget for data version storage.
* Record the dataset version for each model build.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data versioning
* Bad, because Adds tooling and storage
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versioning near code
* Bad, because May not suit image datasets
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No extra tooling
* Bad, because Harder to reproduce builds
* Sources: `d:11`, `v:11.3`
