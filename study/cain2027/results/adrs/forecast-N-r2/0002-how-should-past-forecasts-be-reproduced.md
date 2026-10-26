# How should past forecasts be reproduced?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires reproducibility for any past week, so inputs, code, configuration, and model artifacts must be traceable over time.

## Decision Drivers

* Past-week reproducibility
* Weekly run

## Considered Options

* Versioned data and model artifacts
* Recompute from current state

## Decision Outcome

Chosen option: "Versioned data and model artifacts".

Versioning the inputs, code, configuration, and model artifact gives reruns the historical state needed to reproduce past forecasts.

### Consequences

* Historical inputs and artifacts must be retained.
* Pipeline changes need version tracking.

## Pros and Cons of the Options

### Versioned data and model artifacts

* Good, because Supports reruns
* Good, because Clear lineage
* Bad, because Requires artifact storage
* Bad, because Needs version discipline

### Recompute from current state

* Good, because Simple storage
* Good, because Few components
* Bad, because Past inputs may change
* Bad, because Results can drift
