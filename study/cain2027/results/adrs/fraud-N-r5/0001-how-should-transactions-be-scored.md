# How should transactions be scored?

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction needs a fraud score before authorization, with a response in tens of milliseconds.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-ms latency

## Considered Options

* Synchronous request-response scoring
* Asynchronous scoring

## Decision Outcome

Chosen option: "Synchronous request-response scoring".

A synchronous response makes the score available in time for authorization and fits the stated latency requirement.

### Consequences

* Authorization path depends on scoring response.
* Latency must be managed across feature retrieval and inference.

## Pros and Cons of the Options

### Synchronous request-response scoring

* Good, because Score available before authorization
* Good, because Direct latency measurement
* Bad, because Authorization depends on service health

### Asynchronous scoring

* Good, because Decouples service availability
* Good, because Buffers bursts
* Bad, because Score may arrive too late
