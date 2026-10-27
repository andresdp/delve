# Scale scoring instances horizontally for transaction peaks

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue scoring transactions during peaks while returning results quickly.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Horizontally scaled service instances
* Single larger service instance

## Decision Outcome

Chosen option: "Horizontally scaled service instances".

Adding instances provides a direct way to handle peak load and reduce dependence on one scoring process.

### Consequences

* The service must distribute requests across instances.

## Pros and Cons of the Options

### Horizontally scaled service instances

* Good, because Adds capacity during peaks
* Good, because Limits single-instance bottlenecks
* Bad, because Requires traffic distribution
* Bad, because Capacity management needed

### Single larger service instance

* Good, because Simpler deployment
* Good, because No cross-instance coordination
* Bad, because Limited peak capacity
* Bad, because Single failure point
