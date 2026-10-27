# Partition batches to parallelize document processing

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents per day create substantial processing demand, and seasonal variation makes it useful to scale processing capacity. The design space identifies partitioning within a pipeline as a parallelization option.

## Decision Drivers

* High throughput
* Seasonal capacity variation

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioned processing better fits the stated daily volume. The checked point has no warnings; the rival point also has no warnings, but no-parallel processing does not address the throughput driver.

### Consequences

* Partitioning strategy must preserve document and result association.
* Capacity must scale with seasonal load.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Parallel work within pipeline
* Good, because Supports throughput scaling
* Bad, because Requires partition coordination
* Sources: `d:17`, `v:17.2`

### No parallel data processing

* Good, because Simple processing flow
* Bad, because Limited throughput scaling
* Sources: `d:17`, `v:17.4`
