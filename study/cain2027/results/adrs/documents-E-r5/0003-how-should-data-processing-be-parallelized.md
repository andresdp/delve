# How should data processing be parallelized?

* System: Large-scale document classification

## Context and Problem Statement

Daily document volume reaches millions and varies seasonally. Partitioning work within the pipeline supports parallel processing in the modeled design options.

## Decision Drivers

* millions of documents
* seasonal variation
* processing throughput

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* Data pipeline per data set (`v:17.1`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning is the most direct modeled option for parallelizing a high-volume pipeline. It was included in both checked points without warnings; neither point had attesting sources.

### Consequences

* Define partition keys and processing ownership.
* Coordinate retries and aggregation across partitions.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because enables parallel processing
* Good, because scales across partitions
* Bad, because requires partition management
* Sources: `d:17`, `v:17.2`

### Data pipeline per data set

* Good, because isolates datasets
* Good, because allows separate pipelines
* Bad, because multiplies pipeline operations
* Sources: `d:17`, `v:17.1`

### No parallel data processing

* Good, because simpler operations
* Bad, because limits throughput headroom
* Sources: `d:17`, `v:17.4`
