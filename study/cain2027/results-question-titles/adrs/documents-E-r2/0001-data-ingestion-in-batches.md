# Data ingestion in batches

*How should documents enter the system?*

* System: Large-scale document classification

## Context and Problem Statement

The classifier must handle millions of documents each day, with volume varying through the year.

## Decision Drivers

* high daily volume
* seasonal variation

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch intake suits large, seasonally variable volumes; the brief does not require immediate results. The design point had no warnings, though no combination was attested by sources.

### Consequences

* Intake runs must absorb seasonal peaks.
* Results become available after processing batches.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because supports grouped intake
* Good, because fits batch workloads
* Bad, because results wait for batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because continuous intake
* Good, because supports low latency
* Bad, because requires stream operations
* Sources: `d:7`, `v:7.1`
