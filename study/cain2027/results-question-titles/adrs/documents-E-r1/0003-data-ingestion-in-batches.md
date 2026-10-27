# Data ingestion in batches

*How should incoming documents be ingested and processed?*

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly across the year, making predictable bulk processing and capacity adjustment important. The brief does not specify an immediate classification deadline.

## Decision Drivers

* Millions per day
* Seasonal volume
* Classification quality

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion and processing match the stated scale and accommodate seasonal workload planning without assuming a real-time requirement. The checked batch design point has no warnings; its combination is novel (`attested_by` is empty).

### Consequences

* Processing latency depends on batch frequency.
* Batch sizing and schedule must account for seasonal peaks.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Fits bulk inputs
* Good, because Can schedule for demand
* Bad, because Adds wait time
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous arrival handling
* Good, because Can reduce queue delay
* Bad, because Requires stream operations
* Sources: `d:7`, `v:7.1`
