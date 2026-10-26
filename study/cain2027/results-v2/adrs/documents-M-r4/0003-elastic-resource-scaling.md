# Elastic resource scaling

*How should compute capacity respond to seasonal workload?*

* System: Large-scale document classification

## Context and Problem Statement

Demand swings seasonally, so the system must handle peaks without keeping peak capacity idle year-round. No hard cost or latency target is stated.

## Decision Drivers

* Seasonal demand swings
* Daily volume
* Compute cost

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Seasonal demand and daily volume favor automatic scaling, supported by “Productionizing Machine Learning with a Microservices Architecture” and “Architecting a Machine Learning Pipeline.” This gives up the maximum idle-capacity savings of scale-to-zero; the checked point had no warnings but was unattested.

### Consequences

* Capacity policies must account for seasonal peaks and batch windows.
* Operating cost varies with workload.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Seasonal demand: scales compute with workload
* Good, because Daily volume: supports larger processing peaks
* Bad, because Compute cost: scaling policy needs tuning
* Sources: `s02_p01`, `s04_p02`, `s04_p06`, `s13_p09`, `s13_p10`, `s15_p04`, `s21_p15`

### Scale-to-zero serving

* Good, because Compute cost: removes idle serving capacity
* Bad, because Daily volume: cold starts may delay resumed work
* Sources: `s11_p04`, `s13_p09`, `s13_p10`
