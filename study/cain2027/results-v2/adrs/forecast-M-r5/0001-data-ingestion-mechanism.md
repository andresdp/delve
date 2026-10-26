# Data ingestion mechanism

* System: Retail demand forecasting

## Context and Problem Statement

Weekly store and product demand forecasts need historical data available to repeat past runs. The brief gives no real-time input requirement.

## Decision Drivers

* Reproduce past weeks
* Protect weekly run

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

Reproducibility decides: ETL fits the stated weekly cadence and avoids adding a streaming freshness requirement. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” discuss batch ingestion; the checked point has no warnings, though no source attests to the full combination.

### Consequences

* Retain dated input snapshots for past-week reruns.
* Forecast data refresh follows the batch schedule.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Reproducibility: batch extracts support repeatable inputs
* Bad, because Weekly run: waits for batch completion
* Sources: `s02_p12`, `s04_p04`

### Streaming feature ingestion

* Good, because Freshness: continuous feature updates
* Bad, because Reproducibility: requires retained event history
* Sources: `s02_p04`, `s04_p11`
