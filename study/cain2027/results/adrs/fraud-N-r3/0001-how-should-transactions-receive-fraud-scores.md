# How should transactions receive fraud scores?

* System: Card-fraud scoring service

## Context and Problem Statement

Authorization needs a score before it proceeds, with response times in the tens of milliseconds. The service must handle peaks without making scoring depend on slow asynchronous processing.

## Decision Drivers

* Pre-authorization scoring
* Tens-of-milliseconds latency
* Peak traffic

## Considered Options

* Synchronous scoring API
* Asynchronous scoring queue

## Decision Outcome

Chosen option: "Synchronous scoring API".

A synchronous API provides the score within the authorization flow and suits the stated latency need. Its request path must be designed for low overhead.

### Consequences

* Authorization depends on scoring availability.
* Queueing and feature retrieval must avoid long waits.

## Pros and Cons of the Options

### Synchronous scoring API

* Good, because Fits authorization flow
* Good, because Returns score immediately
* Bad, because Adds authorization-path dependency

### Asynchronous scoring queue

* Good, because Buffers traffic spikes
* Good, because Decouples callers
* Bad, because Score may arrive too late
