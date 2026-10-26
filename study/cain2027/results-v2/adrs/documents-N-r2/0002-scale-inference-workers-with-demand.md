# Scale inference workers with demand

* System: Large-scale document classification

## Context and Problem Statement

Volume varies strongly over the year, so fixed inference capacity risks either peak shortfalls or idle capacity off peak.

## Decision Drivers

* Elasticity: seasonal peaks
* Throughput: millions/day
* Cost: capacity utilization

## Considered Options

* Autoscaled worker fleet
* Fixed-capacity fleet

## Decision Outcome

Chosen option: "Autoscaled worker fleet".

Seasonal elasticity decides the choice; some scale-up lag and policy complexity are accepted to avoid sizing permanently for peak demand.

### Consequences

* Scaling needs safe bounds and queue-aware signals.
* Peak capacity still requires an explicit target.

## Pros and Cons of the Options

### Autoscaled worker fleet

* Good, because Elasticity: capacity follows demand
* Good, because Cost: reduce idle capacity
* Bad, because Latency: scale-up lag
* Bad, because Operations: scaling policy tuning

### Fixed-capacity fleet

* Good, because Latency: predictable capacity
* Good, because Operations: simpler sizing
* Bad, because Cost: idle off-peak capacity
* Bad, because Throughput: peak overload risk
