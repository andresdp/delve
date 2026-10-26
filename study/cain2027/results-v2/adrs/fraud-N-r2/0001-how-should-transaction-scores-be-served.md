# How should transaction scores be served?

* System: Card-fraud scoring service

## Context and Problem Statement

Scores are needed before authorization, with a response time of tens of milliseconds. The brief does not specify deployment topology, but the scoring path must keep inference overhead low.

## Decision Drivers

* Low latency
* Peak availability

## Considered Options

* Synchronous in-process inference
* Dedicated online scoring service

## Decision Outcome

Chosen option: "Synchronous in-process inference".

Low latency is the top driver, so avoiding a network hop takes priority; this gives up independent scaling and failure isolation.

### Consequences

* Deploy inference alongside the authorization path.
* Coordinate capacity and failure handling with callers.

## Pros and Cons of the Options

### Synchronous in-process inference

* Good, because Low latency: avoids a network hop
* Bad, because Peak availability: shares failure and resource limits with callers

### Dedicated online scoring service

* Good, because Peak availability: can scale independently
* Bad, because Low latency: adds a network hop
