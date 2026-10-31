# Scheduled batch prediction deployment

*How should forecasts be delivered?*

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly per store and product, with no stated requirement for request-time predictions. A scheduled scoring run can produce results for downstream use.

## Decision Drivers

* weekly cadence
* store-product coverage
* operational simplicity

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

The weekly cadence supports scheduled batch scoring and the brief gives no low-latency requirement. “Three Levels of ML Software” and “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” describe batch prediction delivery; the checked point selected this option, though it also flags the unresolved ingestion decision.

### Consequences

* Publish a dated forecast set after each successful run.
* Consumers read persisted results.
* Define handling for late or failed runs.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because fits weekly scoring
* Good, because writes results for reuse
* Bad, because results wait for next run
* Bad, because requires batch failure recovery
* Sources: `s01_p08`, `s02_p02`, `s19_p14`

### Online computation serving

* Good, because fresh request-time results
* Good, because supports interactive consumers
* Bad, because adds serving operations
* Bad, because unneeded for stated cadence
* Sources: `s02_p02`, `s04_p10`, `s12_p02`
