# Scale classification resources elastically with demand

* System: Large-scale document classification

## Context and Problem Statement

Incoming volume varies strongly over the year, so fixed capacity risks either peak-period bottlenecks or idle capacity.

## Decision Drivers

* Seasonal volume
* Millions of documents daily
* Capacity efficiency

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Vertically scalable training (`v:3.1`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling matches the seasonal workload pattern. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Productionizing Machine Learning with a Microservices Architecture” discuss scaling resources with workload demand.

### Consequences

* Define scaling thresholds and maximum capacity.
* Track utilization and processing backlog across seasons.
* Validate scaling behavior against peak volume.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adapts capacity to demand
* Good, because Supports workload peaks
* Bad, because Scaling policy needs tuning
* Bad, because Peak capacity still costs more
* Sources: `s02_p01`, `s04_p06`

### Vertically scalable training

* Good, because Simple capacity model
* Good, because Fewer distributed components
* Bad, because Bounded by machine size
* Bad, because Does not directly address variable serving load
* Sources: `s02_p01`
