# Process classifications asynchronously

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive per day, and volume varies strongly over the year. A synchronous request path could make callers wait on variable inference capacity.

## Decision Drivers

* Millions/day throughput
* Seasonal cost
* Multi-team access

## Considered Options

* Queue-backed workers
* Synchronous service

## Decision Outcome

Chosen option: "Queue-backed workers".

Millions/day throughput decides the choice: queued work can be processed in parallel and buffered through bursts. This gives up immediate results and requires queue operations.

### Consequences

* Callers submit work and retrieve results later.
* Retries and failure handling must avoid duplicate outcomes.

## Pros and Cons of the Options

### Queue-backed workers

* Good, because Throughput: absorb bursts and parallelize inference
* Good, because Cost: scale workers with queue depth
* Bad, because Latency: queueing adds delay
* Bad, because Operations: queue and retry handling

### Synchronous service

* Good, because Latency: immediate result when capacity is available
* Good, because Operations: simpler request path
* Bad, because Throughput: callers contend for inference capacity
* Bad, because Cost: peak capacity may sit idle off-season
