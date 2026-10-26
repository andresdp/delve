# How should documents be ingested?

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with volume varying by season. The brief does not specify whether arrivals are continuous or provided in scheduled batches.

## Decision Drivers

* Millions per day
* Seasonal volume swings

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion matches the scale and accommodates seasonal volume by adjusting batch size. The design-space check had no warnings, though the combination is unattested.

### Consequences

* Classification results are produced after ingestion batches run.
* Batch sizing and cadence need operational tuning.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Fits scheduled high-volume loads
* Good, because Supports variable batch sizes
* Bad, because Results wait for a batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous intake
* Good, because Supports low-latency processing
* Bad, because Requires stream operations
* Sources: `d:7`, `v:7.1`
