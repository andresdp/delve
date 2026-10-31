# Batch-based data processing

*How to process documents*

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly over the year, requiring a processing approach that can manage large workloads. The brief does not specify real-time classification.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Batch processing matches the high, variable volume without assuming a latency need absent from the brief (d:15, v:15.1). The batch design point had no warnings; it was unattested, as was the streaming rival.

### Consequences

* Scale workers with batch load.
* Classification results are not immediate.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Fits grouped workloads
* Bad, because Results may be delayed
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes continuously
* Bad, because More operational complexity
* Sources: `d:15`, `v:15.2`
