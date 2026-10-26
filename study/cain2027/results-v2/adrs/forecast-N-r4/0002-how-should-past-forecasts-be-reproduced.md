# How should past forecasts be reproduced?

* System: Retail demand forecasting

## Context and Problem Statement

The system must reproduce forecasts for any past week; doing so requires preserving the inputs and model state used for each run.

## Decision Drivers

* Forecast reproducibility
* Weekly run reliability
* End-to-end ownership

## Considered Options

* Version data, code, configuration, and model artifacts per run
* Keep only the latest data and model

## Decision Outcome

Chosen option: "Version data, code, configuration, and model artifacts per run".

Forecast reproducibility decides the choice; retaining each run’s dependencies costs storage and lifecycle management.

### Consequences

* Each run must record immutable input and artifact references.
* Retention policy affects storage needs.

## Pros and Cons of the Options

### Version data, code, configuration, and model artifacts per run

* Good, because Forecast reproducibility: retain complete run inputs
* Good, because Weekly run reliability: identifiable artifacts
* Bad, because End-to-end ownership: storage and versioning overhead

### Keep only the latest data and model

* Good, because End-to-end ownership: minimal artifact management
* Bad, because Forecast reproducibility: past runs cannot be reconstructed
