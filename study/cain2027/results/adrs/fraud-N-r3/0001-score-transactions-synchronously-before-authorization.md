# Score transactions synchronously before authorization

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a fraud score within tens of milliseconds, so scoring must complete in the transaction path. The score must be available before the authorization decision proceeds.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency

## Considered Options

* Synchronous request-response scoring
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous request-response scoring".

A synchronous call makes the score available before authorization; its added latency must fit within the stated tens-of-milliseconds budget.

### Consequences

* Authorization depends on scoring response time.
* The scoring path needs a strict latency budget.

## Pros and Cons of the Options

### Synchronous request-response scoring

* Good, because Score gates authorization
* Good, because Immediate result
* Bad, because Adds path latency

### Asynchronous scoring

* Good, because Decouples services
* Good, because Buffers bursts
* Bad, because Score arrives later
* Bad, because Cannot gate authorization
