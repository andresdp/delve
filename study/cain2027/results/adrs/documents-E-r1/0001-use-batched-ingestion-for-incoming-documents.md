# Use batched ingestion for incoming documents

* System: Large-scale document classification

## Context and Problem Statement

The classifier receives millions of documents per day, with volume varying strongly by season. The brief gives no requirement for immediate classification.

## Decision Drivers

* High volume
* Seasonal volume shifts
* No latency target

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion fits the stated volume pattern, and the brief does not require real-time results. The checked point has no warnings; the rival streaming point also has no warnings, so the choice follows the batch scale and unspecified latency drivers.

### Consequences

* Classification runs on batch arrival or schedule.
* Batch size and cadence need operational tuning.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Handles grouped workloads
* Good, because Fits scheduled capacity
* Bad, because Adds processing delay
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous arrival handling
* Good, because Low ingestion delay
* Bad, because Always-on processing demand
* Sources: `d:7`, `v:7.1`
