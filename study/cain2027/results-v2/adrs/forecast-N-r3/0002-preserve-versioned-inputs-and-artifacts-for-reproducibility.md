# Preserve versioned inputs and artifacts for reproducibility

* System: Retail demand forecasting

## Context and Problem Statement

The team must reproduce forecasts for any past week. That requires retaining enough information about the data and model used for each run to recreate its outputs.

## Decision Drivers

* Forecast reproducibility
* Weekly-run reliability

## Considered Options

* Versioned data, code, configuration, and model artifacts
* Keep only the latest data and model

## Decision Outcome

Chosen option: "Versioned data, code, configuration, and model artifacts".

Forecast reproducibility decides the choice: retaining versioned run inputs and artifacts enables past forecasts to be recreated. This costs storage and additional artifact management.

### Consequences

* Each run must record references to its data, code, configuration, and model.
* Retention and artifact storage need ongoing ownership.

## Pros and Cons of the Options

### Versioned data, code, configuration, and model artifacts

* Good, because Forecast reproducibility: records each run's inputs and artifacts
* Good, because Weekly-run reliability: supports reruns from recorded state
* Bad, because Forecast reproducibility: requires storage and retention practices

### Keep only the latest data and model

* Good, because Weekly-run reliability: minimal artifact management
* Bad, because Forecast reproducibility: past runs may not be recreated
