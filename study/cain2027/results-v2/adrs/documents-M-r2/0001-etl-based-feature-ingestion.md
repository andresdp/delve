# ETL-based feature ingestion

*How should source documents enter the workflow?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, but the brief does not require predictions at request time. The ingestion path must handle volume while feeding repeatable classification runs.

## Decision Drivers

* High daily volume
* Seasonal capacity swings

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

Daily volume favors batch loading, consistent with the scalable data processing described in “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture.” This gives up immediate ingestion freshness, which the brief does not require.

### Consequences

* Process documents in scheduled batches.
* Size batch windows to seasonal peaks.
* Define an acceptable arrival-to-classification delay.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because High volume: batch extraction and transformation
* Bad, because Freshness: waits for the next load
* Sources: `s02_p12`, `s04_p04`

### Streaming feature ingestion

* Good, because Freshness: continuous event intake
* Bad, because Cost: continuous processing capacity
* Sources: `s04_p03`, `s06_p02`
