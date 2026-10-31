# Version input data and code for reproducible weekly forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, so each run needs traceable inputs and implementation. The brief does not prescribe a storage or versioning technology.

## Decision Drivers

* Past-week reproducibility
* End-to-end ownership

## Considered Options

* Record immutable data snapshots and code versions per run
* Rebuild from current source data

## Decision Outcome

Chosen option: "Record immutable data snapshots and code versions per run".

This directly supports replaying a past week with its original inputs and code. The additional storage and versioning work fits a small team better than relying on mutable sources.

### Consequences

* Each run records data and code versions.
* Historical snapshots require retention and storage.

## Pros and Cons of the Options

### Record immutable data snapshots and code versions per run

* Good, because Traceable inputs
* Good, because Repeatable runs
* Bad, because Snapshot storage cost
* Bad, because Versioning upkeep

### Rebuild from current source data

* Good, because Simple pipeline
* Good, because Less storage
* Bad, because Historical data may change
* Bad, because Past results may drift
