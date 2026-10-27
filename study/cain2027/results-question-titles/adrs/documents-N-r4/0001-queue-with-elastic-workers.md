# Queue with elastic workers

*How should classification work scale with volume?*

* System: Large-scale document classification

## Context and Problem Statement

The system processes millions of incoming documents daily, with strong seasonal variation. Processing capacity must absorb peaks without requiring peak-sized always-on workers.

## Decision Drivers

* Millions daily
* Seasonal volume swings
* Classification throughput

## Considered Options

* Synchronous request path
* Queue with elastic workers

## Decision Outcome

Chosen option: "Queue with elastic workers".

A durable queue absorbs seasonal surges, while independently scalable workers process documents through the LLM classifier. This fits high daily volume without tying submitters to inference latency.

### Consequences

* Callers must handle delayed results.
* Queue depth and worker capacity need monitoring.

## Pros and Cons of the Options

### Synchronous request path

* Good, because Simple request flow
* Good, because Immediate response
* Bad, because Peak load strains service
* Bad, because Caller waits on inference

### Queue with elastic workers

* Good, because Buffers volume spikes
* Good, because Workers scale independently
* Bad, because Results arrive asynchronously
* Bad, because Queue operations add complexity
