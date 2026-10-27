# Data partitioning in data pipeline

*How should data processing be parallelized?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents per day call for parallel work, with seasonal changes in volume. Partitioning a pipeline allows work within a workload to run concurrently.

## Decision Drivers

* Millions per day
* Seasonal volume
* Throughput

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning directly supports parallel processing of the large batch workload. The checked alternative combination produced no warnings, though the design space attests to neither complete combination (`attested_by` is empty).

### Consequences

* Partition sizing affects throughput and overhead.
* Processing must preserve document and result association.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Parallelizes within a pipeline
* Good, because Scales work across partitions
* Bad, because Partitioning needs coordination
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because Separates dataset workloads
* Good, because Independent pipeline runs
* Bad, because More pipelines to operate
* Sources: `d:17`, `v:17.1`
