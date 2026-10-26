# Data partitioning in data pipeline

*How should data processing be parallelized?*

* System: Large-scale document classification

## Context and Problem Statement

Processing millions of documents makes parallel work relevant, and seasonal volume swings make the ability to scale throughput important.

## Decision Drivers

* High daily volume
* Seasonal volume swings

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

High daily volume decides in favor of partitioning to enable parallel processing. This costs tuning effort as volume changes seasonally.

### Consequences

* The pipeline must partition and coordinate document work.
* Partition sizing may need seasonal adjustment.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because High daily volume: partitions enable parallel processing
* Bad, because Seasonal capacity: partition sizing needs tuning
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because Seasonal capacity: scale pipelines by data set
* Bad, because High daily volume: separate pipelines add overhead
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Bad, because High daily volume: processing remains serial
* Sources: `d:17`, `v:17.4`
