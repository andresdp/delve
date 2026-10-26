# Runtime capacity scaling

* System: Large-scale document classification

## Context and Problem Statement

Classification volume changes substantially across the year, so fixed capacity risks either peak overload or idle resources. The brief does not specify infrastructure or budget limits.

## Decision Drivers

* Seasonal volume
* Serving cost
* Throughput

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Replicated mutable model instances (`v:26.4`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Seasonal volume decides the choice: elastic capacity can track demand, with cost control as a secondary benefit. This gives up the predictability of a fixed replica pool; “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” support demand-scaled resources.

### Consequences

* Capacity limits and scaling behavior need operational tuning.
* Peak workloads may still queue while capacity grows.
* The checked design point is novel and unattested.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Seasonal volume: capacity follows workload demand
* Good, because Serving cost: reduces unused capacity
* Bad, because Throughput: scaling may lag sudden bursts
* Bad, because Serving cost: added scaling controls and capacity planning
* Sources: `s02_p01`, `s04_p02`, `s04_p06`, `s13_p09`, `s13_p10`, `s15_p04`, `s21_p15`

### Replicated mutable model instances

* Good, because Throughput: replicas can serve work concurrently
* Good, because Seasonal volume: capacity can be increased by adding instances
* Bad, because Serving cost: replicas consume capacity while running
* Bad, because Operations: mixed evidence and mutable replicas add coordination
