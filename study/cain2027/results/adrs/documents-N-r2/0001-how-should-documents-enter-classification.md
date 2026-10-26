# How should documents enter classification?

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, and demand varies strongly by season. Intake must absorb bursts without coupling submitters to classifier capacity.

## Decision Drivers

* Millions daily
* Seasonal volume
* Multiple teams consume results

## Considered Options

* Durable queue with asynchronous workers
* Synchronous classification API

## Decision Outcome

Chosen option: "Durable queue with asynchronous workers".

A durable queue buffers seasonal peaks and lets classification capacity scale independently of document submitters.

### Consequences

* Results arrive asynchronously.
* Queue retention and retry policy must be set.

## Pros and Cons of the Options

### Durable queue with asynchronous workers

* Good, because Buffers bursts
* Good, because Scales workers independently
* Bad, because Adds processing latency
* Bad, because Requires retry handling

### Synchronous classification API

* Good, because Immediate response
* Good, because Simple request flow
* Bad, because Ties up callers
* Bad, because Burst capacity is harder
