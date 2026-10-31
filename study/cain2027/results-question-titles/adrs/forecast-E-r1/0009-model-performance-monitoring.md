# Model performance monitoring

*What should be monitored in production?*

* System: Retail demand forecasting

## Context and Problem Statement

A broken or degraded forecast could affect a scheduled weekly run, so production behavior needs visibility.

## Decision Drivers

* Forecast reliability
* Operational visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Monitoring model performance gives the team a way to detect forecast degradation in production (d:22, v:22.1).

### Consequences

* The team must define performance measures.
* Monitoring signals need review and response.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks forecast performance
* Good, because Can expose degradation
* Bad, because Needs quality signals
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Good, because No monitoring upkeep
* Bad, because Problems may go unnoticed
* Sources: `d:22`, `v:22.3`
