# Scale inference workers with demand

* System: Large-scale document classification

## Context and Problem Statement

Document volume varies strongly over the year, while the classifier must handle millions of documents per day. Capacity should follow changing demand without requiring permanently provisioned peak compute.

## Decision Drivers

* Seasonal cost
* Millions/day throughput

## Considered Options

* Autoscaled workers
* Fixed peak-sized fleet

## Decision Outcome

Chosen option: "Autoscaled workers".

Seasonal cost decides the choice: autoscaling reduces idle capacity while adding workers for higher volume. This gives up some responsiveness during abrupt demand increases.

### Consequences

* Worker capacity needs a demand signal and scaling limits.
* A backlog may grow while capacity catches up.

## Pros and Cons of the Options

### Autoscaled workers

* Good, because Cost: capacity follows current demand
* Good, because Throughput: add workers during peaks
* Bad, because Latency: scale-up can lag sudden surges
* Bad, because Operations: scaling signals need tuning

### Fixed peak-sized fleet

* Good, because Throughput: peak capacity is always ready
* Good, because Latency: no scale-up delay
* Bad, because Cost: excess capacity off-season
* Bad, because Cost: pay for peak even at low volume
