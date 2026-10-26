# Data ingestion in batches

*How should documents enter the system?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with volume varying strongly over the year. The design space offers batch and streaming ingestion approaches (d:7).

## Decision Drivers

* Seasonal peak scale
* Daily throughput

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Seasonal peak scale decides the choice: batches allow work to be grouped around fluctuating volume. This gives up immediate ingestion and classification.

### Consequences

* Results depend on batch cadence.
* Capacity must handle peak batch volume.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Seasonal peak scale: collect and process in batches
* Bad, because Latency: results wait for a batch run
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Latency: accept documents continuously
* Bad, because Seasonal peak scale: continuous capacity may be harder to right-size
* Sources: `d:7`, `v:7.1`
