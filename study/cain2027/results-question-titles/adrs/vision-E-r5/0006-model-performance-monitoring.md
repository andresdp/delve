# Model performance monitoring

*How should model performance be monitored?*

* System: On-device visual inspection

## Context and Problem Statement

The model runs in production on cameras, and its quality needs to remain visible after updates.

## Decision Drivers

* Production defect detection
* Weekly model updates
* Limited operational capacity

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Monitoring model performance provides a way to assess deployed quality across recurring updates; the design space point was warning-free but unattested.

### Consequences

* The team must define performance signals and review them.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model performance parameters
* Bad, because Requires performance signals
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Captures inputs and outputs
* Bad, because Requires log storage and review
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because No monitoring infrastructure
* Bad, because Production issues may go unnoticed
* Sources: `d:22`, `v:22.3`
