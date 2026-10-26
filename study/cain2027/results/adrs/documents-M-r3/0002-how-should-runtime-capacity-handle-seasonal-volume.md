# How should runtime capacity handle seasonal volume?

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly over the year, so fixed capacity risks either peak overload or unused resources.

## Decision Drivers

* Seasonal demand
* Millions of documents
* Capacity utilization

## Considered Options

* Elastic resource scaling (`v:26.6`)
* CPU-or-GPU resource allocation (`v:26.3`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic capacity directly addresses seasonal changes in classification workload. “Productionizing Machine Learning with a Microservices Architecture” and “Architecting a Machine Learning Pipeline” document automatic scaling with workload demand.

### Consequences

* Scale batch workers with queued work.
* Tune capacity limits and cost controls.
* Measure throughput before setting capacity targets.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Follows workload demand
* Good, because Handles volume changes
* Bad, because Requires scaling controls
* Sources: `s02_p01`, `s04_p02`, `s04_p06`

### CPU-or-GPU resource allocation

* Good, because Explicit compute choice
* Good, because Supports cluster jobs
* Bad, because Does not specify elasticity
