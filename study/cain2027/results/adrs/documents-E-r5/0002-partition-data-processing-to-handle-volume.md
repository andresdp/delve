# Partition data processing to handle volume

* System: Large-scale document classification

## Context and Problem Statement

Daily document volume is large and varies over the year, so processing capacity must scale across workload peaks.

## Decision Drivers

* Millions daily
* Seasonal volume

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning supports processing large batches in parallel; it is the choice in the checked point (d:17, v:17.2).

### Consequences

* Partitions and results need coordination.
* Uneven partitions can constrain throughput.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Parallel work units
* Good, because Supports larger batches
* Bad, because Requires partition coordination
* Sources: `d:17`, `v:17.2`

### No parallel data processing

* Good, because Simpler execution
* Bad, because Limited throughput
* Sources: `d:17`, `v:17.4`
