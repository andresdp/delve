# Process classifications asynchronously

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with strongly seasonal volume. The brief gives no per-document response-time requirement.

## Decision Drivers

* Throughput: millions/day
* Elasticity: seasonal peaks

## Considered Options

* Queue-backed worker pool
* Synchronous request path

## Decision Outcome

Chosen option: "Queue-backed worker pool".

Throughput and seasonal elasticity decide the choice; the system gives up immediate results in exchange for buffering and independently scaled workers.

### Consequences

* Consumers must tolerate delayed results.
* Queue depth and worker capacity need monitoring.

## Pros and Cons of the Options

### Queue-backed worker pool

* Good, because Throughput: parallel consumers
* Good, because Elasticity: scale workers independently
* Bad, because Latency: queue adds delay
* Bad, because Operations: broker to manage

### Synchronous request path

* Good, because Latency: immediate response
* Good, because Operations: simpler flow
* Bad, because Throughput: request path bottleneck
* Bad, because Elasticity: peak capacity harder
