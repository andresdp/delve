# Scale scoring resources elastically for transaction peaks

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue scoring during peaks, while demand may vary. Fixed capacity risks either overload or excess idle resources.

## Decision Drivers

* Peak availability
* Variable demand

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling addresses the peak requirement while keeping the service available. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” describes scaling resources with workload demand; scale-to-zero conflicts with the need for fast scoring availability.

### Consequences

* Set capacity limits and scale signals against latency and throughput.
* Maintain warm serving capacity through quiet periods.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adapts capacity to demand
* Good, because Supports peak throughput
* Bad, because Scaling adds operational complexity
* Bad, because Capacity changes need monitoring
* Sources: `s02_p01`, `s04_p02`, `s04_p06`

### Scale-to-zero serving

* Good, because Reduces idle capacity
* Good, because Lowers quiet-period cost
* Bad, because Cold starts risk latency
* Bad, because Unsuitable for continuous readiness
* Sources: `s11_p04`, `s13_p09`
