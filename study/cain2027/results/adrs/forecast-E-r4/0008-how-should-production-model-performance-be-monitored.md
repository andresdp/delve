# How should production model performance be monitored?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires the weekly run to remain dependable as model ideas enter production, but it does not specify a monitoring approach.

## Decision Drivers

* Production reliability
* Model quality
* Small team

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Monitoring model performance gives the team a signal when production forecasts need attention; the checked combination had no warnings and no attested sources.

### Consequences

* The team must select performance measures and review cadence.
* Monitoring adds recurring operational work.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Surfaces quality changes
* Bad, because Requires ongoing review
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Supports run investigation
* Bad, because Requires storage and review
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Degradation may go unnoticed
* Sources: `d:22`, `v:22.3`
