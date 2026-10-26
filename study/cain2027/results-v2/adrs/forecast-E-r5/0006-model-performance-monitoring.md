# Model performance monitoring

*How to monitor the model in production?*

* System: Retail demand forecasting

## Context and Problem Statement

The weekly forecasting run must continue to work as new ideas reach production. The brief does not state the production monitoring signals or response process.

## Decision Drivers

* Weekly run reliability
* Reproducibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Weekly run reliability decides the choice: monitoring model performance can reveal quality changes after release. The brief does not specify metrics, so choosing and maintaining useful measures remains additional work.

### Consequences

* Select forecast quality measures and alert thresholds.
* Link monitoring results to model and data versions.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Weekly run reliability: surfaces quality changes
* Bad, because Reproducibility: needs linked run and input records
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Reproducibility: records inputs and outputs
* Bad, because Weekly run reliability: logs alone may not detect quality loss
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because Reproducibility: tracks model usage and outputs
* Bad, because Small team: broader tracking needs more upkeep
* Sources: `d:22`, `v:22.4`

### No in-production monitoring

* Good, because Small team: no monitoring setup
* Bad, because Weekly run reliability: failures may remain unnoticed
* Sources: `d:22`, `v:22.3`
