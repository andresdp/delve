# Data partitioning in data pipeline

*How should processing scale across documents?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents per day make serial processing a poor fit, and seasonal peaks require capacity to expand.

## Decision Drivers

* high throughput
* seasonal peaks

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning parallelizes work within the chosen batch flow, directly addressing volume. The alternative checked point also produced no warnings; neither combination was source-attested.

### Consequences

* Partitions need stable assignment and aggregation.
* Peak throughput depends on available workers.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because parallel work within a run
* Good, because fits batch processing
* Bad, because partition coordination required
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because isolates datasets
* Good, because separate run control
* Bad, because duplicates pipeline operations
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Good, because simple execution
* Bad, because limited throughput
* Sources: `d:17`, `v:17.4`
