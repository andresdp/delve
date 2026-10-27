# Version input data and pipeline code for reproducible historical forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, which requires preserving the inputs and implementation used for each run.

## Decision Drivers

* Historical reproducibility
* Weekly forecasts

## Considered Options

* Versioned snapshots and code revisions
* Latest data and code only

## Decision Outcome

Chosen option: "Versioned snapshots and code revisions".

Recording each run's data snapshot and code revision directly supports reproducing forecasts for past weeks.

### Consequences

* Retain or reference each run's inputs and code revision.
* Run records need stable identifiers.

## Pros and Cons of the Options

### Versioned snapshots and code revisions

* Good, because Traceable run inputs
* Good, because Repeatable outputs
* Bad, because Snapshot storage cost
* Bad, because More pipeline metadata

### Latest data and code only

* Good, because Simple operations
* Bad, because Past runs drift
* Bad, because Cannot reproduce inputs
