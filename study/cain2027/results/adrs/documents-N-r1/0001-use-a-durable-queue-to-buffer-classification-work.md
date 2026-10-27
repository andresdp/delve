# Use a durable queue to buffer classification work

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive each day, with strong seasonal volume swings. A queue lets ingestion absorb bursts while workers scale independently.

## Decision Drivers

* Daily volume
* Seasonal peaks
* Throughput

## Considered Options

* Durable queue with worker pool
* Synchronous classification

## Decision Outcome

Chosen option: "Durable queue with worker pool".

Buffering and independent worker scaling address variable load while keeping ingestion decoupled from slower LLM inference.

### Consequences

* Classification becomes asynchronous.
* Track queue age and retry failed work.

## Pros and Cons of the Options

### Durable queue with worker pool

* Good, because Buffers bursts
* Good, because Scales workers independently
* Bad, because Adds queue operations

### Synchronous classification

* Good, because Simple request flow
* Bad, because Ties up callers
* Bad, because Peak load causes delays
