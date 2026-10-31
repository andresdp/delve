# Scale runtime resources elastically with workload demand

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly over the year, so fixed capacity risks either peak-time bottlenecks or unused capacity outside peaks.

## Decision Drivers

* Seasonal volume variation
* Large scoring workload

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Fixed runtime capacity

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling addresses seasonal variation directly. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” support scaling resources with workload demand; the checked design point returned no conflicting warnings.

### Consequences

* Capacity must be monitored as demand changes.
* Resource use and cost will vary with workload.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adjusts capacity to demand
* Good, because Supports variable workloads
* Bad, because Scaling requires operational configuration
* Sources: `s02_p01`, `s04_p02`, `s15_p04`

### Fixed runtime capacity

* Good, because Predictable provisioned capacity
* Bad, because May be underused off-peak
* Bad, because May constrain peak throughput
