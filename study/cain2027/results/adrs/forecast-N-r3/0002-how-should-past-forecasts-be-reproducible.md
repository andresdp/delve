# How should past forecasts be reproducible?

* System: Retail demand forecasting

## Context and Problem Statement

The team must reproduce forecasts for any past week. That requires retaining the inputs and implementation details used for each run.

## Decision Drivers

* Past-week reproducibility
* End-to-end team ownership

## Considered Options

* Versioned run inputs and artifacts
* Keep only latest inputs and model

## Decision Outcome

Chosen option: "Versioned run inputs and artifacts".

Retaining versioned data references, code, configuration, and model artifacts gives the team the information needed to reconstruct a historical run.

### Consequences

* Storage and retention policies are needed.
* Each run needs links to its inputs and artifacts.

## Pros and Cons of the Options

### Versioned run inputs and artifacts

* Good, because Supports reruns
* Good, because Makes runs traceable
* Bad, because Requires artifact retention
* Bad, because Adds version management

### Keep only latest inputs and model

* Good, because Simpler storage
* Bad, because Past runs may be unrecoverable
* Bad, because Results can drift
