# How should past-week forecasts be reproducible?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts to be reproducible for any past week. That requires retaining the inputs and model artifacts used for each run, not only the latest forecast.

## Decision Drivers

* historical reproducibility
* weekly forecasting
* auditability

## Considered Options

* Versioned run snapshots
* Recompute from current data
* Save forecasts only

## Decision Outcome

Chosen option: "Versioned run snapshots".

Snapshots of the data version, configuration, model artifact, and forecast output provide a basis for replaying a past week. Recomputing against mutable current data or retaining outputs alone cannot reliably reproduce the original result.

### Consequences

* Record identifiers for inputs, code, configuration, and model artifacts per run.
* Retain snapshots and artifacts for an agreed period.
* Define whether replay means bit-for-bit or tolerance-based equivalence.

## Pros and Cons of the Options

### Versioned run snapshots

* Good, because preserves inputs and outputs
* Good, because supports replay
* Bad, because storage costs
* Bad, because retention policy needed

### Recompute from current data

* Good, because less stored data
* Good, because simple retention
* Bad, because past data may change
* Bad, because results may drift

### Save forecasts only

* Good, because small storage footprint
* Good, because easy retrieval
* Bad, because cannot replay runs
* Bad, because limited diagnosis
