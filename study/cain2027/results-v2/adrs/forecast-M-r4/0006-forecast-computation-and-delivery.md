# Forecast computation and delivery

* System: Retail demand forecasting

## Context and Problem Statement

The system produces forecasts weekly per store and product; the brief does not require request-time predictions. Batch computation fits the stated cadence and allows forecasts to be stored for use.

## Decision Drivers

* Weekly cadence
* Protect weekly run
* Past-week reproducibility

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

The weekly cadence decides the choice: scheduled batch scoring matches the stated forecast cycle and avoids unnecessary online serving complexity. The trade-off is that forecasts update on the schedule rather than on demand.

### Consequences

* Persist forecast outputs with their run and model versions.
* Provide downstream users a stable location for each weekly forecast set.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Weekly cadence: computes on schedule
* Good, because Reproducibility: results can be stored by run
* Bad, because Freshness: results wait for the next batch
* Sources: `s01_p08`, `s02_p02`

### Online computation serving

* Good, because Freshness: computes on request
* Bad, because Weekly cadence: adds runtime serving complexity
* Sources: `s02_p06`
