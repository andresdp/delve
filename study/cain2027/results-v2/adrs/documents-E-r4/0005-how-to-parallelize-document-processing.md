# How to parallelize document processing

* System: Large-scale document classification

## Context and Problem Statement

The volume reaches millions of documents per day and changes significantly over the year, so processing work needs to scale across partitions.

## Decision Drivers

* High throughput at scale
* Elasticity across seasonal peaks

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

High throughput decides: partitioning allows concurrent processing within a pipeline. We accept the operational work of coordinating partitions.

### Consequences

* Work must be divided and results reconciled.
* Capacity can scale with partitioned workload.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Throughput: partitions work for parallel processing
* Bad, because Operations: partitioning and coordination required
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because Isolation: separate pipeline per dataset
* Bad, because Elasticity: scaling tied to dataset pipelines
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Bad, because Throughput: limits concurrent processing
* Sources: `d:17`, `v:17.4`
