# Partition batch processing to scale throughput

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents each day, with seasonal changes in volume. Processing needs to scale to the incoming workload.

## Decision Drivers

* High daily volume
* Seasonal demand

## Considered Options

* Data partitioning in data pipeline (`v:17.2`)
* No parallel data processing (`v:17.4`)

## Decision Outcome

Chosen option: "Data partitioning in data pipeline" (`v:17.2`).

Partitioning provides a way to increase batch throughput as seasonal volume rises. It was selected in the checked batch point; the rival point using no parallel processing was also unattested (d:17).

### Consequences

* Partitions need to be balanced across workers.
* Results must be gathered for consumers.

## Pros and Cons of the Options

### Data partitioning in data pipeline

* Good, because Enables parallel processing
* Good, because Scales within a pipeline
* Bad, because Requires partition management
* Sources: `d:17`, `v:17.2`

### No parallel data processing

* Good, because Simpler processing flow
* Bad, because Limited throughput scaling
* Sources: `d:17`, `v:17.4`
