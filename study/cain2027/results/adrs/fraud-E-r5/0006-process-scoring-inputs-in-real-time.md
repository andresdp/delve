# Process scoring inputs in real time

* System: Card-fraud scoring service

## Context and Problem Statement

Transaction data must be processed in the authorization path to produce a score within tens of milliseconds. The design space distinguishes real-time stream processing from batch processing.

## Decision Drivers

* Pre-authorization scoring
* Tens of milliseconds

## Considered Options

* Real-time, stream-based data processing (`v:15.2`)
* Batch-based data processing (`v:15.1`)

## Decision Outcome

Chosen option: "Real-time, stream-based data processing" (`v:15.2`).

Real-time processing fits the transaction scoring path. The checked point reported no warnings; the batch rival is inconsistent with scoring each transaction before authorization.

### Consequences

* Keep the live processing path within the latency budget.
* Plan capacity for peak transaction rates.

## Pros and Cons of the Options

### Real-time, stream-based data processing

* Good, because Supports live data processing
* Bad, because Streaming operations required
* Sources: `d:15`, `v:15.2`

### Batch-based data processing

* Good, because Batch workflow
* Bad, because Cannot serve each transaction in time
* Sources: `d:15`, `v:15.1`
