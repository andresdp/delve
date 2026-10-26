# How should compute capacity handle seasonal variation?

* System: Large-scale document classification

## Context and Problem Statement

Workload varies strongly over the year, so fixed capacity risks either peak overload or unused capacity outside peak periods.

## Decision Drivers

* Seasonal volume variation
* Millions of documents daily

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Seasonal volume and daily scale make elastic resource scaling the stronger fit; “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” describe scaling with workload. This favors peak capacity over eliminating all idle serving cost.

### Consequences

* Capacity must be monitored against workload and scaling limits.
* Some capacity may remain allocated between peaks.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Seasonality: adjusts capacity with workload
* Good, because Volume: scales for large processing demand
* Bad, because Operations: requires scaling rules and monitoring
* Sources: `s02_p01`, `s04_p02`, `s04_p06`, `s13_p09`, `s13_p10`, `s15_p04`, `s21_p15`

### Scale-to-zero serving

* Good, because Cost: removes idle serving capacity
* Bad, because Volume: may need capacity startup during peaks
* Sources: `s11_p04`, `s13_p09`, `s13_p10`
