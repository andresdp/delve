# Process transaction inputs in real time

* System: Card-fraud scoring service

## Context and Problem Statement

The fraud score is required before each transaction is authorized. Processing transactions in scheduled batches would delay scores beyond that decision point.

## Decision Drivers

* Score before authorization
* Tens-of-milliseconds response

## Considered Options

* Real-time, stream-based data processing (`v:15.2`)
* Batch-based data processing (`v:15.1`)

## Decision Outcome

Chosen option: "Real-time, stream-based data processing" (`v:15.2`).

Real-time processing fits the per-transaction authorization path; batch processing cannot provide the score in time. This design point is novel and unattested in the space, with no warnings returned.

### Consequences

* Process transactions as they arrive.
* Plan for sustained and peak event volumes.

## Pros and Cons of the Options

### Real-time, stream-based data processing

* Good, because Processes incoming events
* Good, because Fits real-time decisions
* Bad, because Continuous processing operations
* Bad, because Peak capacity planning
* Sources: `d:15`, `v:15.2`

### Batch-based data processing

* Good, because Scheduled workloads
* Good, because Batch efficiency
* Bad, because Results arrive later
* Bad, because Cannot gate each transaction
* Sources: `d:15`, `v:15.1`
