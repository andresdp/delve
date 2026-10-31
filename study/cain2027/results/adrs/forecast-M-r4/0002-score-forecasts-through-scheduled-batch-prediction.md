# Score forecasts through scheduled batch prediction

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts by store and product, with no request-time prediction requirement in the brief.

## Decision Drivers

* Weekly forecasts
* Reproducible past weeks

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

Scheduled batch scoring fits the stated weekly forecast cadence; “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software” describe scheduled or precomputed prediction patterns (s02_p12, s19_p14).

### Consequences

* Forecast results are refreshed on the weekly schedule.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Fits weekly cadence
* Good, because Writes results to storage
* Bad, because Forecasts update on schedule
* Sources: `s01_p08`, `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`

### Online computation serving

* Good, because Uses current request context
* Good, because Fresh per request
* Bad, because Requires online serving
