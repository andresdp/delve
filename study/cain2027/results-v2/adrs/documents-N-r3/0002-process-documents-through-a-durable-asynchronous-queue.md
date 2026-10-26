# Process documents through a durable asynchronous queue

* System: Large-scale document classification

## Context and Problem Statement

Millions of classifications per day and seasonal peaks make synchronous, tightly coupled processing difficult to scale. A queue can buffer bursts and let workers scale with demand.

## Decision Drivers

* Millions of documents per day
* Seasonal volume variation

## Considered Options

* Durable queue with autoscaled workers
* Synchronous classification service

## Decision Outcome

Chosen option: "Durable queue with autoscaled workers".

Millions per day and seasonal variation decide in favor of buffering and elastic workers; this adds queue operations and can increase end-to-end latency.

### Consequences

* Workers need retry and idempotency handling.
* Queue depth becomes a capacity signal.

## Pros and Cons of the Options

### Durable queue with autoscaled workers

* Good, because Scale: add workers for peaks
* Good, because Seasonality: buffer bursts
* Bad, because Cost: queue and worker operations

### Synchronous classification service

* Good, because Simplicity: direct request flow
* Bad, because Scale: caller-bound throughput
* Bad, because Seasonality: peak capacity required
