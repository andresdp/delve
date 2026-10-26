# How to monitor classification quality

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. That calls for monitoring model performance in production.

## Decision Drivers

* Detect quality drift
* Operator visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring directly addresses the brief’s requirement to expose quality drift (d:22, v:22.1). The chosen batch design point had no warnings and was unattested; the streaming rival was also unattested.

### Consequences

* Choose quality measures and alert thresholds.
* Monitoring depends on timely quality signals.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks performance measures
* Bad, because Requires quality signals
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Bad, because Logs alone may not show quality
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because Tracks usage and outputs
* Bad, because Broader tracking scope
* Sources: `d:22`, `v:22.4`
