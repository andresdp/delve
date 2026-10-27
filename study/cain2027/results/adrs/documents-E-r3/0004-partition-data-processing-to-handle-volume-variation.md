# Partition data processing to handle volume variation

* System: Large-scale document classification

## Context and Problem Statement

Daily volume is in the millions and varies over the year. The design space includes partitioned processing as an option for parallelizing data processing (d:17).

## Decision Drivers

* Millions of documents daily
* Seasonal volume variation

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning is the design-space option that directly supports parallel processing, which suits the stated high and variable volume. The checked combination had no warnings, but was unattested.

### Consequences

* Choose partitioning and workload limits.
* Coordinate aggregation of partition results.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Enables parallel processing
* Good, because Can scale with batch size
* Bad, because Requires partition coordination
* Sources: `d:17`, `v:17.2`

### No parallel data processing

* Good, because Simpler execution path
* Bad, because Limits processing throughput
* Sources: `d:17`, `v:17.4`
