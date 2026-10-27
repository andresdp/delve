# Streaming feature ingestion

*How should incoming documents enter processing?*

* System: Large-scale document classification

## Context and Problem Statement

The brief describes high, variable daily volume, so intake should be able to absorb bursts and feed classification independently of document arrival rate.

## Decision Drivers

* High daily volume
* Seasonal bursts

## Considered Options

* Streaming feature ingestion (`v:21.2`)
* ETL-based feature ingestion (`v:21.1`)

## Decision Outcome

Chosen option: "Streaming feature ingestion" (`v:21.2`).

Choose streaming ingestion to accommodate changing arrival rates. The design point check found this combination unattested, so this is a brief-driven choice rather than a source-attested combination.

### Consequences

* Define durable retention and replay separately.
* Monitor intake lag and processing backlog.

## Pros and Cons of the Options

### Streaming feature ingestion

* Good, because Accepts continuous arrivals
* Good, because Supports event-driven processing
* Bad, because Requires stream operations
* Bad, because Long-term retention needs a separate plan
* Sources: `s04_p03`, `s06_p02`

### ETL-based feature ingestion

* Good, because Familiar batch flow
* Good, because Fits scheduled processing
* Bad, because Data may wait for batch runs
* Bad, because Peak arrivals may build up
* Sources: `s02_p02`
