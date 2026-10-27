# Version inputs and artifacts to reproduce forecasts for past weeks

* System: Retail demand forecasting

## Context and Problem Statement

Past-week forecasts must be reproducible, so each run needs a stable record of its input data and model state.

## Decision Drivers

* Past-week reproducibility
* End-to-end team ownership

## Considered Options

* Versioned run inputs and artifacts
* Use current data and model code

## Decision Outcome

Chosen option: "Versioned run inputs and artifacts".

Recording the data snapshot, code or model version, and run configuration makes a past forecast repeatable.

### Consequences

* Each run must retain identifying metadata.
* Historical inputs and model artifacts require retention.

## Pros and Cons of the Options

### Versioned run inputs and artifacts

* Good, because Supports replay
* Good, because Makes runs auditable
* Bad, because Requires artifact storage
* Bad, because Adds run metadata

### Use current data and model code

* Good, because Minimal storage
* Good, because Simple setup
* Bad, because Past runs can change
* Bad, because Hard to debug
