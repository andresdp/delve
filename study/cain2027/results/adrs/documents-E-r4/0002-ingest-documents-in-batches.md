# Ingest documents in batches

* System: Large-scale document classification

## Context and Problem Statement

The brief specifies large daily document volumes but no continuous arrival or latency constraint. Batch and streamed ingestion are both represented in the design space (d:7).

## Decision Drivers

* Millions of documents daily
* Seasonal volume changes
* No latency target specified

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion aligns with batch serving and the brief's lack of an immediate classification requirement. The checked batch point produced no conflict warning for this choice.

### Consequences

* Ingestion cadence sets result freshness.
* Seasonal capacity must cover peak loads.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Supports large scheduled loads
* Good, because Can automate ingestion
* Bad, because Waits for batch availability
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous arrivals
* Good, because Low processing delay
* Bad, because Adds stream operations
* Sources: `d:7`, `v:7.1`
