# How to ingest and process transaction data?

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scoring occurs on each transaction, so fresh data must be available on the online path (d:7, d:15).

## Decision Drivers

* Tens-of-ms latency
* Peak availability

## Considered Options

* Streamed ingestion with real-time processing (`v:7.1`)
* Batch ingestion with batch processing (`v:7.3`)

## Decision Outcome

Chosen option: "Streamed ingestion with real-time processing" (`v:7.1`).

Tens-of-ms scoring on current transactions decides the choice: streaming keeps inputs fresh, at the cost of additional processing operations. The selected point pairs streamed ingestion with real-time processing (v:15.2).

### Consequences

* Operate continuous ingestion and processing.
* Keep feature computation off the critical scoring path where possible.

## Pros and Cons of the Options

### Streamed ingestion with real-time processing

* Good, because Latency: continuously updated inputs
* Bad, because Peak availability: stream processing adds operational load
* Sources: `d:7`, `v:7.1`, `d:15`, `v:15.2`

### Batch ingestion with batch processing

* Good, because Peak availability: process off the request path
* Bad, because Latency: data may be stale
* Sources: `d:7`, `v:7.3`, `d:15`, `v:15.1`
