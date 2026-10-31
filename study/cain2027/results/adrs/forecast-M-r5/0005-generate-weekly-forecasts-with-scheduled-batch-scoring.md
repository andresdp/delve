# Generate weekly forecasts with scheduled batch scoring

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand by store and product, with no requirement for request-time predictions. Batch scoring fits the stated cadence and makes forecast runs easier to reproduce.

## Decision Drivers

* Weekly cadence
* Store-product forecasts
* No real-time requirement

## Considered Options

* Online computation serving (`v:31.5`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

This accepted option matches the weekly forecast cadence and was included in the checked point. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Three Levels of ML Software” describe scheduled batch prediction patterns.

### Consequences

* Forecast outputs must be stored with their run identity.
* Consumers receive updates on the weekly schedule.

## Pros and Cons of the Options

### Online computation serving

* Good, because Fresh request-time results
* Good, because Supports interactive use
* Bad, because Adds runtime complexity
* Bad, because Not required by the brief

### Scheduled batch prediction deployment

* Good, because Matches weekly schedule
* Good, because Writes results for downstream use
* Bad, because Results refresh on schedule
* Bad, because Requires run and output tracking
* Sources: `s02_p02`, `s02_p12`, `s19_p14`
