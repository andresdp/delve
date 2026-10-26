# How should processing scale across the document workload?

* System: Large-scale document classification

## Context and Problem Statement

Daily volume is in the millions and varies over the year, so processing needs to run in parallel to handle peaks.

## Decision Drivers

* High throughput
* Variable volume
* Cost efficiency

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

High throughput decides the choice: partitioning enables parallel work within the pipeline. The trade-off is added coordination overhead, which must be weighed against throughput and peak capacity needs.

### Consequences

* Choose partition keys and manage skewed workloads.
* Provision parallel capacity for seasonal peaks.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because High throughput: partitions enable parallel processing
* Good, because Variable volume: distribute work across available capacity
* Bad, because Cost efficiency: partitioning and coordination add overhead
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because Operational isolation: dedicated pipeline per dataset
* Bad, because Variable volume: scaling across pipelines may be uneven
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Good, because Cost efficiency: no parallel processing overhead
* Bad, because High throughput: limited processing capacity
* Sources: `d:17`, `v:17.4`
