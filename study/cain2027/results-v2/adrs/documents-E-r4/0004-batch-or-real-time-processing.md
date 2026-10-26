# Batch or real-time processing

* System: Large-scale document classification

## Context and Problem Statement

The system processes a large, seasonally variable volume, and no strict response-time target is stated.

## Decision Drivers

* High throughput at scale
* Elasticity across seasonal peaks

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Throughput decides: batch processing matches bulk document intake and seasonal load variation. The cost is delayed results between processing runs.

### Consequences

* Processing capacity can be allocated per run.
* A backlog may build between runs.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Throughput: processes accumulated work
* Bad, because Freshness: waits for scheduled processing
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Freshness: processes arrivals continuously
* Bad, because Cost: steady stream-processing capacity
* Sources: `d:15`, `v:15.2`
