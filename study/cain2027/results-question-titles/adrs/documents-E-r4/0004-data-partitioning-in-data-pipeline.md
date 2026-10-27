# Data partitioning in data pipeline

*How should data processing scale across the workload?*

* System: Large-scale document classification

## Context and Problem Statement

Daily volume is large and changes substantially over the year. Partitioning work within a pipeline provides a design-space option for parallel processing.

## Decision Drivers

* High daily volume
* Seasonal volume swings

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning is a direct fit for parallelizing a high-volume workload and can accommodate seasonal increases. The checked point raised no warnings and had no attesting sources.

### Consequences

* Partitions and worker capacity need tuning.
* Uneven partitions can slow batch completion.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Enables parallel processing
* Good, because Scales work within a pipeline
* Bad, because Requires partition management
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because Separates dataset workflows
* Good, because Allows independent pipeline runs
* Bad, because Adds pipeline overhead
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Good, because Simpler execution model
* Bad, because Limits throughput headroom
* Sources: `d:17`, `v:17.4`
