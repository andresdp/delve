# How should runtime capacity respond to seasonal demand?

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly over the year, so fixed capacity risks either peak-time bottlenecks or idle resources outside peaks.

## Decision Drivers

* Seasonal capacity swings
* High daily volume

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Seasonal capacity swings decide the choice: elastic scaling fits variable workloads, as described in “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture.” It may cost more during peaks than scaling to zero, but keeps capacity available when document volume rises.

### Consequences

* Set scaling limits for peak periods.
* Monitor queue depth and job completion time.
* Provisioning changes can lag sudden demand spikes.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Seasonal capacity: compute follows workload demand
* Good, because High volume: expands for large jobs
* Bad, because Cost: peak capacity may be expensive
* Sources: `s02_p01`, `s04_p02`, `s15_p04`

### Scale-to-zero serving

* Good, because Cost: removes idle serving capacity
* Bad, because Seasonal capacity: startup can delay work
* Sources: `s11_p04`, `s13_p09`
