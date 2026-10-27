# Prediction serving mode

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts per store and product, with no request-time prediction requirement in the brief.

## Decision Drivers

* Weekly forecast cadence
* Store and product coverage
* Reproducibility

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Scheduled batch scoring matches the stated weekly demand forecast cadence and avoids adding an unstated online serving need. Support includes “Architecting a Machine Learning Pipeline” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning.”

### Consequences

* Forecast publication depends on successful scheduled scoring.
* Forecasts are refreshed at the batch cadence.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Fits weekly scoring
* Good, because Persists forecast outputs
* Bad, because Results refresh on schedule
* Bad, because Requires batch completion monitoring
* Sources: `s02_p02`, `s02_p12`, `s25_p06`

### Online computation serving

* Good, because Fresh on request
* Good, because Supports interactive use
* Bad, because Unstated latency need
* Bad, because More runtime complexity
