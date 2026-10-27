# Use an asynchronous queue to scale document classification

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, with strong seasonal volume swings. Classification can be decoupled from ingestion so processing capacity can scale with demand.

## Decision Drivers

* Millions per day
* Seasonal volume
* Classification throughput

## Considered Options

* Synchronous API calls
* Asynchronous queue with scalable workers

## Decision Outcome

Chosen option: "Asynchronous queue with scalable workers".

A queue absorbs seasonal surges and lets classification capacity scale independently of incoming document volume.

### Consequences

* Classification is eventually available.
* Queue lag and worker capacity need monitoring.

## Pros and Cons of the Options

### Synchronous API calls

* Good, because Simple request flow
* Bad, because Couples ingestion to inference
* Bad, because Harder to absorb peaks

### Asynchronous queue with scalable workers

* Good, because Buffers demand peaks
* Good, because Scales workers independently
* Bad, because Adds queue operations
* Bad, because Results arrive later
