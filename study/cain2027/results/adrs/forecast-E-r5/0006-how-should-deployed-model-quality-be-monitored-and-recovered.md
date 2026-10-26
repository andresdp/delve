# How should deployed model quality be monitored and recovered?

* System: Retail demand forecasting

## Context and Problem Statement

A new model must not break the weekly run, so production quality needs observation and a recovery path. The design space covers performance monitoring and rollback as separate decisions.

## Decision Drivers

* Protect weekly run
* Model iteration
* Reproducibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Monitoring forecast performance helps detect degraded releases. Pair this with rollback to the previous model version (d:10, v:10.2), which restores a known model when needed; the combined checked point has no warnings and is unattested.

### Consequences

* Define forecast performance measures and review them after runs.
* Retain a deployable previous model version.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model performance
* Bad, because Requires performance measures
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Bad, because Requires log management
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because No monitoring overhead
* Bad, because Issues may go unnoticed
* Sources: `d:22`, `v:22.3`
