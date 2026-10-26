# Runtime capacity scaling

* System: Large-scale document classification

## Context and Problem Statement

Seasonal volume shifts make fixed compute capacity a poor fit for classification workloads. Capacity should respond to demand while handling large processing volumes.

## Decision Drivers

* Seasonal volume
* Millions of documents
* Capacity efficiency

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Choose elastic scaling to match compute capacity to the brief’s seasonal workload swings. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” discuss scaling resources with demand.

### Consequences

* Set peak and scale limits.
* Monitor scaling behavior and cost.
* Batch schedules must account for capacity ramp-up.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Follows workload demand
* Good, because Handles changing capacity needs
* Bad, because Requires scaling policies
* Bad, because Peak capacity can be costly
* Sources: `s02_p01`, `s04_p02`, `s13_p09`, `s15_p04`

### Scale-to-zero serving

* Good, because Reduces idle serving cost
* Bad, because May add startup delay
* Bad, because Evidence focuses on serving
* Sources: `s11_p04`, `s13_p09`
