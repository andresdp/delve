# Data ingestion in batches

*How should documents be ingested?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of incoming documents and strong seasonal volume swings make ingestion throughput and load handling central. The brief gives no latency target.

## Decision Drivers

* High daily volume
* Seasonal volume swings

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)
* Data ingestion by request (`v:7.2`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

High daily volume and seasonal swings decide in favor of batch intake, which supports scheduled capacity. This gives up immediate processing; the brief does not require low latency.

### Consequences

* Results become available after batch processing.
* Batch scheduling must accommodate seasonal peaks.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Seasonal capacity: collect and schedule batches
* Bad, because Freshness: results wait for the batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Freshness: continuous intake
* Bad, because Seasonal capacity: continuous processing demand
* Sources: `d:7`, `v:7.1`

### Data ingestion by request

* Good, because Control: fetch data when needed
* Bad, because High daily volume: repeated retrieval overhead
* Sources: `d:7`, `v:7.2`
