# Stateless service with horizontal scaling

*How should the scoring service handle peaks?*

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during peaks while returning scores within tens of milliseconds.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Stateless service with horizontal scaling
* Fixed-capacity service

## Decision Outcome

Chosen option: "Stateless service with horizontal scaling".

Horizontal scaling can add scoring capacity during peaks; keeping instances stateless supports replacement and scaling.

### Consequences

* Shared dependencies must also handle peak load.
* Capacity and scaling behavior need operational monitoring.

## Pros and Cons of the Options

### Stateless service with horizontal scaling

* Good, because Scales across instances
* Good, because Instances can be replaced
* Bad, because Requires shared dependencies
* Bad, because Scaling takes resources

### Fixed-capacity service

* Good, because Predictable capacity
* Good, because Simple deployment
* Bad, because Peak saturation risk
* Bad, because Idle capacity off-peak
