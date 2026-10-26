# How to ingest incoming documents

* System: Large-scale document classification

## Context and Problem Statement

The classifier receives millions of documents daily, so ingestion must handle sustained high volume. The brief gives no latency requirement.

## Decision Drivers

* Millions daily
* Variable volume

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion suits the stated volume, and the brief does not require immediate results (d:7, v:7.3). The batch design point had no warnings; it was unattested, as was the streaming rival.

### Consequences

* Process documents on a schedule.
* Tune batch size and cadence to volume.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Groups high volume
* Good, because Fits batch processing
* Bad, because Results arrive later
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous intake
* Bad, because Needs stream operations
* Sources: `d:7`, `v:7.1`
