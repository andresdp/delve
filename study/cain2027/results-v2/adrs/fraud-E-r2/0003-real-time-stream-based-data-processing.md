# Real-time, stream-based data processing

*Should transaction features be processed in batch or in real time?*

* System: Card-fraud scoring service

## Context and Problem Statement

The authorization decision requires a score for the current transaction, while batch processing produces results on a schedule. The design space distinguishes batch and stream-based processing (d:15).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Real-time, stream-based data processing (`v:15.2`)
* Batch-based data processing (`v:15.1`)

## Decision Outcome

Chosen option: "Real-time, stream-based data processing" (`v:15.2`).

Latency decides: the current transaction must be processed online to score it before authorization. This costs more operational complexity than scheduled batch processing.

### Consequences

* The transaction feature path must operate continuously.
* Stream processing details and recovery behavior need definition.

## Pros and Cons of the Options

### Real-time, stream-based data processing

* Good, because Latency: process incoming transactions online
* Bad, because Availability: streaming path adds operational dependencies
* Sources: `d:15`, `v:15.2`

### Batch-based data processing

* Good, because Cost: process data in scheduled groups
* Bad, because Latency: cannot serve the current authorization
* Sources: `d:15`, `v:15.1`
