# Monitor model performance in production

* System: Retail demand forecasting

## Context and Problem Statement

A weekly production run needs a way to detect when model behavior degrades after release. The design space includes model performance monitoring, prediction logging, and production tracking.

## Decision Drivers

* Reliable weekly run
* Detect regression

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring gives the team a signal for detecting forecast degradation after a candidate is promoted.

### Consequences

* Review performance signals as part of weekly operations.
* Choose production measures and thresholds.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model quality
* Bad, because Needs quality signals
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Provides run inputs and outputs
* Bad, because Logs need storage and review
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because Less operational setup
* Bad, because Regressions may go unnoticed
* Sources: `d:22`, `v:22.3`

### Model in-production tracking

* Good, because Tracks usage, inputs, and outputs
* Bad, because Adds tracking overhead
* Sources: `d:22`, `v:22.4`
