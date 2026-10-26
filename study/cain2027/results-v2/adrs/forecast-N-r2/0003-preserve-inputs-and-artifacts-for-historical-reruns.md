# Preserve inputs and artifacts for historical reruns

* System: Retail demand forecasting

## Context and Problem Statement

The retailer must reproduce forecasts for any past week. Reproduction depends on retaining the data, code, configuration, and model artifact associated with each forecast run.

## Decision Drivers

* Historical reproducibility
* Operational simplicity

## Considered Options

* Versioned run records
* Latest data and model only

## Decision Outcome

Chosen option: "Versioned run records".

Historical reproducibility decides the choice; retaining versioned inputs and artifacts costs storage and requires disciplined run recording.

### Consequences

* Each run needs a stable identifier and manifest.
* Historical inputs and artifacts require retention.

## Pros and Cons of the Options

### Versioned run records

* Good, because Historical reproducibility: retain inputs and artifacts
* Good, because Operational simplicity: one run manifest
* Bad, because Operational simplicity: storage retention overhead

### Latest data and model only

* Good, because Operational simplicity: minimal storage
* Bad, because Historical reproducibility: past outputs drift or disappear
