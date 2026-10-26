# Version inputs, code, and model artifacts

*How should historical forecasts be reproducible?*

* System: Retail demand forecasting

## Context and Problem Statement

The team must recreate forecasts for any past week. The brief gives no data or artifact store, so this decision defines the versioning practice, not its implementation.

## Decision Drivers

* Reproducibility
* Small team operations

## Considered Options

* Version inputs, code, and model artifacts
* Keep only the latest inputs and model

## Decision Outcome

Chosen option: "Version inputs, code, and model artifacts".

Reproducibility is the decisive driver: retain the exact inputs, code, and model for each run, accepting the storage and process overhead.

### Consequences

* Each run needs an immutable reference to its inputs and artifacts.
* Storage and retention policy must be decided.

## Pros and Cons of the Options

### Version inputs, code, and model artifacts

* Good, because Reproducibility: records each run's inputs and artifacts
* Bad, because Small team operations: requires versioning discipline

### Keep only the latest inputs and model

* Good, because Small team operations: little maintenance
* Bad, because Reproducibility: past runs may be impossible to recreate
