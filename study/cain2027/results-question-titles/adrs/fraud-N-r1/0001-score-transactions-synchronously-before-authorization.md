# Score transactions synchronously before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

The service must return a score within tens of milliseconds, before each transaction is authorized.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous inline scoring
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous inline scoring".

Inline scoring makes the result available for the authorization decision and keeps latency within the stated budget.

### Consequences

* Authorization depends on scoring response time.
* Scoring capacity must handle transaction traffic.

## Pros and Cons of the Options

### Synchronous inline scoring

* Good, because Score available before authorization
* Good, because Direct latency control
* Bad, because Adds authorization-path dependency

### Asynchronous scoring

* Good, because Decouples request path
* Good, because Absorbs bursts
* Bad, because Score arrives too late
