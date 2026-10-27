# Ingest and process transaction data as streams

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring is required for each transaction as it arrives, leaving little time for scheduled or manual data handling.

## Decision Drivers

* Per-transaction scoring
* Real-time data
* Low latency

## Considered Options

* Streamed data ingestion (`v:7.1`)
* Data ingestion in batches (`v:7.3`)

## Decision Outcome

Chosen option: "Streamed data ingestion" (`v:7.1`).

Continuous ingestion aligns with scoring transactions as they arrive; batch ingestion would delay them (d:7, v:7.1, v:7.3).

### Consequences

* The ingestion path must handle continuous traffic.
* Stream processing needs to fit the scoring latency budget.

## Pros and Cons of the Options

### Streamed data ingestion

* Good, because Continuous data flow
* Good, because Fits incoming transactions
* Bad, because Requires stream handling
* Sources: `d:7`, `v:7.1`

### Data ingestion in batches

* Good, because Processes grouped data
* Good, because Can be partly automated
* Bad, because Delayed availability
* Sources: `d:7`, `v:7.3`
