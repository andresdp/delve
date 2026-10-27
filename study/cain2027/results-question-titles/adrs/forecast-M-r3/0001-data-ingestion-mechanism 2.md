# Data ingestion mechanism

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts need a repeatable way to bring store and product data into the pipeline.

## Decision Drivers

* Weekly cadence
* Past-week reproducibility

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

The weekly forecast cadence fits batch extraction and loading; streaming freshness is not required by the brief. Practitioner support includes “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture.”

### Consequences

* Pipeline must retain or identify each input snapshot.
* Upstream schema changes need handling.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Batch friendly
* Good, because Repeatable input loads
* Bad, because Upstream schema coupling
* Sources: `s02_p12`, `s04_p04`

### Streaming feature ingestion

* Good, because Continuous freshness
* Good, because Event driven
* Bad, because More operational complexity
