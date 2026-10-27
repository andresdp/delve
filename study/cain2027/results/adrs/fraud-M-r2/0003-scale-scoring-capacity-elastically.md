# Scale scoring capacity elastically

* System: Card-fraud scoring service

## Context and Problem Statement

Transaction volume peaks require additional serving capacity, while fixed capacity can leave the service unable to handle demand. The design space supports automatic resource scaling but does not specify a scaling policy.

## Decision Drivers

* Traffic peaks
* Service availability

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Service resource and latency profiling (`v:26.8`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Choose elastic scaling to address peak demand; profiling is useful for sizing but does not provide capacity by itself. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Productionizing Machine Learning with a Microservices Architecture” support elastic scaling. The checked primary point was unattested and had no warnings.

### Consequences

* Set scaling thresholds against measured latency and load.
* Keep enough warm capacity to meet the response budget.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Capacity follows demand
* Good, because Supports peak handling
* Bad, because Scaling thresholds need tuning
* Sources: `s02_p01`, `s04_p02`

### Service resource and latency profiling

* Good, because Measures latency and resource use
* Good, because Informs sizing
* Bad, because Does not itself add capacity
* Sources: `s04_p02`, `s22_p11`
