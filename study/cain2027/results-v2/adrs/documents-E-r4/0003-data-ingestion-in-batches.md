# Data ingestion in batches

*How to ingest incoming documents*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, but the brief gives no requirement for continuous, per-document processing.

## Decision Drivers

* High throughput at scale
* Elasticity across seasonal peaks

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)
* Data ingestion by request (`v:7.2`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

High throughput decides: batch intake groups work efficiently and the brief does not demand immediate classification. This gives up continuous arrival handling.

### Consequences

* Intake and classification cadence must be coordinated.
* Batch sizes can be adjusted for seasonal volume.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Throughput: groups documents for bulk intake
* Bad, because Availability: intake may wait for a batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Availability: receives a continuous stream
* Bad, because Cost: continuous processing capacity
* Sources: `d:7`, `v:7.1`

### Data ingestion by request

* Good, because Cost: fetch only when requested
* Bad, because Throughput: request coordination at scale
* Sources: `d:7`, `v:7.2`
