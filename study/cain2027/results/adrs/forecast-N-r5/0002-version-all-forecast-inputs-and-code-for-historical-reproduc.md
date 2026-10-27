# Version all forecast inputs and code for historical reproducibility

* System: Retail demand forecasting

## Context and Problem Statement

The team must reproduce forecasts for any past week. That requires preserving the data, configuration, and code state used for each run.

## Decision Drivers

* Past-week reproducibility
* End-to-end ownership

## Considered Options

* Versioned inputs, code, and run configuration
* Keep only the latest data and code

## Decision Outcome

Chosen option: "Versioned inputs, code, and run configuration".

Reproduction depends on restoring the full state of a run, not merely rerunning current code against changed data.

### Consequences

* Each run records immutable input and code versions.
* Historical artifacts require retention and storage.

## Pros and Cons of the Options

### Versioned inputs, code, and run configuration

* Good, because Recreates past runs
* Good, because Supports audit
* Bad, because Requires storage discipline
* Bad, because Adds run metadata

### Keep only the latest data and code

* Good, because Less storage
* Good, because Simple operations
* Bad, because Past runs drift
* Bad, because Cannot reliably reproduce
