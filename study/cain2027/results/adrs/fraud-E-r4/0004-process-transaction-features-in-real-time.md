# Process transaction features in real time

* System: Card-fraud scoring service

## Context and Problem Statement

The model must score transactions before authorization, making batch processing unsuitable for the primary scoring path. Real-time processing is an explicit workspace alternative. (d:15)

## Decision Drivers

* Pre-authorization deadline
* Continuous transaction flow

## Considered Options

* Real-time, stream-based data processing (`v:15.2`)
* Batch-based data processing (`v:15.1`)

## Decision Outcome

Chosen option: "Real-time, stream-based data processing" (`v:15.2`).

Real-time feature processing aligns with scoring before authorization. The rival point using batch processing also returned no warnings, but conflicts with the brief’s timing requirement. (d:15, v:15.2)

### Consequences

* Feature computation becomes part of the latency budget.
* Peak traffic requires processing capacity to scale.

## Pros and Cons of the Options

### Real-time, stream-based data processing

* Good, because Fresh features
* Good, because Fits online scoring
* Bad, because More operational complexity
* Bad, because Sensitive to stream delays
* Sources: `d:15`, `v:15.2`

### Batch-based data processing

* Good, because Simpler scheduled work
* Good, because Efficient bulk processing
* Bad, because Cannot meet per-transaction deadline
* Bad, because Features may be stale
* Sources: `d:15`, `v:15.1`
