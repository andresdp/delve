# Ingest documents in batches

* System: Large-scale document classification

## Context and Problem Statement

Incoming volume reaches millions per day and varies over the year. The brief does not specify a real-time response requirement.

## Decision Drivers

* High daily volume
* Seasonal demand

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion matches the batch serving choice and enables processing capacity to be scaled around seasonal demand. The checked batch combination and the real-time rival were both unattested (d:7, d:15).

### Consequences

* Ingestion schedules must accommodate seasonal peaks.
* Consumers receive results after processing completes.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Collects documents for bulk processing
* Good, because Supports scheduled ingestion
* Bad, because Documents wait for a batch
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous input
* Good, because Can feed real-time processing
* Bad, because Requires continuous processing
* Sources: `d:7`, `v:7.1`
