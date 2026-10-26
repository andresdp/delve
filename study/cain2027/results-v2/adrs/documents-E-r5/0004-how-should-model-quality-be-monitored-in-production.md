# How should model quality be monitored in production?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts, so the system needs production monitoring that surfaces model performance changes.

## Decision Drivers

* Detect quality drift

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Detect quality drift decides in favor of monitoring model performance. It requires defining performance measures and may require labeled outcomes to assess quality.

### Consequences

* Operators need performance measures and drift thresholds.
* Quality signals must be made available to operators.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Detect quality drift: observe model performance
* Bad, because Operational visibility: requires performance measures
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Operational visibility: logs inputs and predictions
* Bad, because Detect quality drift: logs alone may not measure quality
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Detect quality drift: no production signal
* Sources: `d:22`, `v:22.3`
