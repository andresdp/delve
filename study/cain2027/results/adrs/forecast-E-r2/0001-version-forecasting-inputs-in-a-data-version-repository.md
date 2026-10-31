# Version forecasting inputs in a data version repository

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, so each run needs a traceable snapshot of its input data. The design space offers a dedicated data version repository, code repository versioning, or no data versioning (d:11).

## Decision Drivers

* Past-week reproducibility
* Traceable inputs

## Considered Options

* Data version repository (`v:11.1`)
* Data versioning in code repository (`v:11.2`)
* No data versioning (`v:11.3`)

## Decision Outcome

Chosen option: "Data version repository" (`v:11.1`).

A data version repository directly supports repeatable forecasts by preserving the inputs used for each run (d:11, v:11.1). The checked point had no warnings; it was unattested, while the rival point without versioning was also unattested.

### Consequences

* Record the input data version with each forecast run.
* Maintain the repository and its retention policy.

## Pros and Cons of the Options

### Data version repository

* Good, because Dedicated data history
* Good, because Supports input traceability
* Bad, because Additional tooling
* Bad, because Storage overhead
* Sources: `d:11`, `v:11.1`

### Data versioning in code repository

* Good, because Keeps versions near code
* Good, because Simple workflow
* Bad, because May couple data and code
* Bad, because Unclear fit for large data
* Sources: `d:11`, `v:11.2`

### No data versioning

* Good, because No added tooling
* Good, because Less storage overhead
* Bad, because Past runs hard to reproduce
* Bad, because Input lineage is weak
* Sources: `d:11`, `v:11.3`
