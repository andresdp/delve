# Runtime capacity strategy

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring demand varies, and the service must remain available during peaks without letting latency grow beyond the brief’s budget.

## Decision Drivers

* Peak demand
* Tens-of-ms latency
* Capacity elasticity

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)
* Service resource and latency profiling (`v:26.8`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling addresses peak demand; profiling should inform its capacity settings. In “Productionizing Machine Learning with a Microservices Architecture,” practitioners also describe profiling service latency and resources.

### Consequences

* Maintain warm capacity to avoid scaling delays.
* Set scaling thresholds against measured latency and load.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adapts capacity to demand
* Good, because Practitioner evidence
* Bad, because Scaling delay requires headroom
* Sources: `s02_p01`, `s04_p02`

### Scale-to-zero serving

* Good, because Reduces idle capacity
* Bad, because Cold starts threaten latency
* Bad, because Not grounded by brief constraints

### Service resource and latency profiling

* Good, because Measures latency and resource use
* Good, because Informs capacity sizing
* Bad, because Requires representative workloads
* Sources: `s04_p02`, `s22_p11`
