# How should documents be ingested?

* System: Large-scale document classification

## Context and Problem Statement

The classifier receives millions of documents daily, with volume varying over the year. The brief gives no latency requirement.

## Decision Drivers

* high volume
* seasonal variation
* unspecified latency

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion fits the stated high volume, and the brief does not require immediate classification. The design point check returned no warnings; it had no attesting sources.

### Consequences

* Schedule or trigger ingestion runs.
* Buffer documents between runs.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because handles grouped workloads
* Good, because fits batch processing
* Bad, because results arrive after ingestion
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because continuous intake
* Good, because low ingestion delay
* Bad, because adds streaming operations
* Sources: `d:7`, `v:7.1`
