# Scale the scoring service horizontally

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during transaction peaks while meeting a tight response-time target. Multiple serving instances can add capacity and reduce reliance on a single instance.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Horizontally scaled serving instances
* Single larger serving instance

## Decision Outcome

Chosen option: "Horizontally scaled serving instances".

Peak availability decides the choice: distributing serving capacity avoids depending on one instance. The trade-off is more deployment and coordination complexity.

### Consequences

* The service must distribute requests across instances.
* Capacity management must account for peak demand.

## Pros and Cons of the Options

### Horizontally scaled serving instances

* Good, because Peak availability: capacity can be distributed across instances
* Good, because Low latency: concurrent requests handled in parallel
* Bad, because Peak availability: instance coordination adds operational complexity

### Single larger serving instance

* Good, because Low latency: avoids cross-instance coordination
* Bad, because Peak availability: one instance limits capacity and creates a failure point
