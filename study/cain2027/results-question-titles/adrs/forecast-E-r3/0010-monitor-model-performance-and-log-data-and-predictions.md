# Monitor model performance and log data and predictions

*How should production forecasts be monitored?*

* System: Retail demand forecasting

## Context and Problem Statement

The weekly run must remain dependable as new models are introduced. Monitoring model performance and logging inputs and predictions can be combined.

## Decision Drivers

* Weekly run reliability
* Model quality
* Reproducibility

## Considered Options

* Monitor model performance and log data and predictions
* Model in-production tracking (`v:22.4`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Monitor model performance and log data and predictions".

Performance monitoring plus run and prediction logs help the team assess forecast quality and investigate past runs (d:22, v:22.1, v:22.2).

### Consequences

* Monitoring needs actual outcomes when available.
* Logs need retention and access policies.

## Pros and Cons of the Options

### Monitor model performance and log data and predictions

* Good, because Tracks forecast quality
* Good, because Supports run investigation
* Bad, because Needs data retention
* Sources: `d:22`, `v:22.1`, `v:22.2`

### Model in-production tracking

* Good, because Tracks usage and outputs
* Bad, because Broader tracking overhead
* Sources: `d:22`, `v:22.4`

### No in-production monitoring

* Good, because Less operational setup
* Bad, because Issues harder to detect
* Sources: `d:22`, `v:22.3`
