# Ingest transaction data as a stream

* System: Card-fraud scoring service

## Context and Problem Statement

The system scores every incoming transaction, so inputs need to reach the ML application continuously. The workspace offers streamed, request-based, and batch ingestion alternatives. (d:7)

## Decision Drivers

* Every transaction
* Real-time scoring

## Considered Options

* Streamed data ingestion (`v:7.1`)
* Data ingestion by request (`v:7.2`)

## Decision Outcome

Chosen option: "Streamed data ingestion" (`v:7.1`).

Continuous ingestion fits scoring each transaction as it arrives. The point check returned no warnings, though it was unattested. (d:7, v:7.1)

### Consequences

* The ingestion path needs resilient stream handling.
* The brief does not specify event ordering or replay requirements.

## Pros and Cons of the Options

### Streamed data ingestion

* Good, because Continuous inputs
* Good, because Fits transaction flow
* Bad, because Stream operations
* Bad, because Requires handling delivery failures
* Sources: `d:7`, `v:7.1`

### Data ingestion by request

* Good, because Explicit retrieval
* Good, because Simple request flow
* Bad, because Per-request retrieval overhead
* Bad, because Can delay scoring
* Sources: `d:7`, `v:7.2`
