# Prediction delivery mode

* System: Retail demand forecasting

## Context and Problem Statement

The product requires a forecast once per week for each store and product, with no online request or low-latency requirement stated. A scheduled scoring job can publish a complete forecast set.

## Decision Drivers

* Weekly cadence
* Store-product coverage
* Operational simplicity

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Scheduled batch scoring directly fits weekly demand forecasts and avoids operating a request-serving path not required by the brief. “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software” discuss scheduled batch prediction; the checked point has no warnings but is unattested.

### Consequences

* Publish forecasts as a versioned weekly output.
* Define behavior for incomplete or failed scoring runs.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Matches weekly cadence
* Good, because Writes complete result set
* Bad, because Results refresh on schedule
* Bad, because Requires batch completion monitoring
* Sources: `s01_p08`, `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`

### Online computation serving

* Good, because Fresh per request
* Good, because Interactive responses
* Bad, because Unneeded serving complexity
* Bad, because No real-time requirement
