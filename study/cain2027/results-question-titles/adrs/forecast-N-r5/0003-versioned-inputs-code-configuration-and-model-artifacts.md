# Versioned inputs, code, configuration, and model artifacts

*What must be recorded to reproduce a past forecast?*

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts to be reproducible for any past week. Reproduction depends on retaining the inputs and implementation details used for each run.

## Decision Drivers

* Past-week reproducibility
* Weekly pipeline

## Considered Options

* Versioned inputs, code, configuration, and model artifacts
* Store forecasts only

## Decision Outcome

Chosen option: "Versioned inputs, code, configuration, and model artifacts".

Retaining the run’s inputs and implementation state enables regeneration of historical forecasts rather than only retrieving saved outputs.

### Consequences

* Each run needs links to its data and artifact versions.
* Historical inputs and artifacts require retention and retrieval.

## Pros and Cons of the Options

### Versioned inputs, code, configuration, and model artifacts

* Good, because Supports reruns
* Good, because Makes changes traceable
* Bad, because Requires retained artifacts
* Bad, because Adds metadata management

### Store forecasts only

* Good, because Simple retention
* Good, because Fast historical lookup
* Bad, because Cannot regenerate outputs
* Bad, because Weak audit trail
