# Scheduled batch pipeline

*How should forecasts run?*

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly for each store and product. The weekly run must complete reliably without slowing model development.

## Decision Drivers

* Weekly cadence
* Store-product forecasts
* Protect weekly run

## Considered Options

* Scheduled batch pipeline
* Online per-request inference

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

A scheduled batch pipeline matches the weekly forecast cadence and keeps production execution separate from experimentation.

### Consequences

* Forecasts update on the weekly schedule.
* The pipeline needs monitoring and recovery for failed runs.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Fits weekly cadence
* Good, because Runs independently
* Bad, because Results arrive in batches

### Online per-request inference

* Good, because On-demand results
* Bad, because Unneeded request infrastructure
* Bad, because More operational complexity
