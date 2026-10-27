# Scale scoring service instances horizontally

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue scoring during peaks while responding within tens of milliseconds.

## Decision Drivers

* Peak traffic
* Low latency
* Continued availability

## Considered Options

* Horizontally scaled service instances
* Single larger service instance

## Decision Outcome

Chosen option: "Horizontally scaled service instances".

Additional instances provide a direct way to absorb peaks and avoid relying on one scoring process.

### Consequences

* Instances should avoid local state needed by other requests.
* Capacity management and load balancing are required.

## Pros and Cons of the Options

### Horizontally scaled service instances

* Good, because Add capacity for peaks
* Good, because Distribute requests
* Bad, because Requires load balancing

### Single larger service instance

* Good, because Simpler deployment
* Bad, because Limited peak capacity
* Bad, because Single failure point
