# Version input data for reproducible forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Past weekly forecasts must be reproducible. The design space offers repository based data versioning and alternatives without data versioning (d:11).

## Decision Drivers

* Reproduce past weeks
* Protect weekly run

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

Reproducing a past week is the deciding driver, so retain explicit data versions despite the added workflow. The design point combining this with model quality testing, rollback, and scheduled runs returned no warnings, but no attesting sources.

### Consequences

* Record the data version used for each forecast run.
* Maintain storage and retrieval for historical data versions.

## Pros and Cons of the Options

### Data version repository

* Good, because Reproducibility: records data versions
* Bad, because Delivery speed: adds versioning work
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Reproducibility: tracks data with code
* Bad, because Delivery speed: adds repository workflow
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because Delivery speed: no versioning setup
* Bad, because Reproducibility: past inputs may be unavailable
* Sources: `d:11`, `v:11.3`
