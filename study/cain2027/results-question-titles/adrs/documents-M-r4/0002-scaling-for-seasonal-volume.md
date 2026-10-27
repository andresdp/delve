# Scaling for seasonal volume

* System: Large-scale document classification

## Context and Problem Statement

Classification demand varies strongly over the year, so capacity needs to respond to workload changes. The brief does not specify a hosting platform or latency target.

## Decision Drivers

* seasonal demand
* millions of documents
* resource efficiency

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling directly addresses seasonal workload variation and large processing volumes. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” support scaling compute with demand.

### Consequences

* Capacity follows workload demand.
* Scaling behavior and limits need operational configuration.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because adjusts capacity to demand
* Good, because supports large workloads
* Bad, because requires scaling configuration
* Sources: `s02_p01`, `s04_p02`, `s15_p04`

### Scale-to-zero serving

* Good, because reduces idle serving cost
* Bad, because may not suit scheduled batch capacity
* Sources: `s13_p09`
