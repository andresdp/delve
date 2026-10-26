# How should runtime capacity respond to seasonal demand?

* System: Large-scale document classification

## Context and Problem Statement

Classification demand varies strongly over the year, so fixed capacity risks either insufficient peak capacity or unused off-peak resources.

## Decision Drivers

* Seasonal volume
* Cost

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Seasonal volume decides the choice: elastic resources adjust to workload demand, as described in “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture.” This gives up some cost simplicity because scaling behavior needs tuning.

### Consequences

* Monitor workload and capacity to tune scaling.
* Peak throughput depends on available infrastructure.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Seasonal volume: capacity follows workload demand
* Bad, because Cost: scaling policy needs tuning
* Sources: `s02_p01`, `s04_p02`, `s04_p06`

### Scale-to-zero serving

* Good, because Cost: removes idle serving capacity
* Bad, because Seasonal volume: cold starts may slow resumed scoring
* Sources: `s11_p04`, `s13_p09`, `s13_p10`
