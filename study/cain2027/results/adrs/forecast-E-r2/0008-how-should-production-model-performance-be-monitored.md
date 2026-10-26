# How should production model performance be monitored?

* System: Retail demand forecasting

## Context and Problem Statement

The weekly run must remain dependable as new models are introduced. Monitoring model performance can reveal degradation that warrants investigation or rollback. [d:22, v:22.1]

## Decision Drivers

* Weekly run reliability
* Safe releases

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring directly supports checking whether released models continue to produce acceptable forecasts across weekly runs. [d:22, v:22.1]

### Consequences

* Choose forecast quality measures and review thresholds.
* Monitoring results require an operational response.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks forecast quality
* Good, because Can flag degradation
* Bad, because Needs performance measures and review
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Bad, because Logs alone do not assess model quality
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because Tracks use and model behavior
* Bad, because Broader tracking overhead
* Sources: `d:22`, `v:22.4`
