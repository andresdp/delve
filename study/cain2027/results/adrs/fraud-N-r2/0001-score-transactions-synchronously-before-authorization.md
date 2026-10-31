# Score transactions synchronously before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores must be available before a transaction is authorized, within tens of milliseconds.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous request-response scoring
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous request-response scoring".

The authorization path needs the score before it can proceed, and the latency target supports a bounded synchronous call.

### Consequences

* Authorization depends on scoring availability.
* The scoring endpoint needs a strict latency budget.

## Pros and Cons of the Options

### Synchronous request-response scoring

* Good, because Score available for authorization
* Good, because Simple request flow
* Bad, because Scoring latency delays authorization

### Asynchronous scoring

* Good, because Decouples scoring work
* Bad, because Score may arrive too late
