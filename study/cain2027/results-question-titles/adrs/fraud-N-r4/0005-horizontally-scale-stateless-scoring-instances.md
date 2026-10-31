# Horizontally scale stateless scoring instances

*How should scoring handle traffic peaks?*

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during peaks as well as return scores quickly. Capacity management and overload behavior determine whether the authorization path remains usable under load.

## Decision Drivers

* Peak availability
* Tens-of-milliseconds latency

## Considered Options

* Horizontally scale stateless scoring instances
* Fixed-capacity scoring pool

## Decision Outcome

Chosen option: "Horizontally scale stateless scoring instances".

Horizontal scaling provides a way to add capacity for peaks and reduce dependence on individual instances. It requires load management and capacity headroom to protect the latency target.

### Consequences

* Serving instances should not hold required transaction state locally.
* Scaling thresholds and overload behavior need definition.

## Pros and Cons of the Options

### Horizontally scale stateless scoring instances

* Good, because Adds serving capacity
* Good, because Limits instance-level failure
* Bad, because Needs capacity headroom
* Bad, because Depends on shared state availability

### Fixed-capacity scoring pool

* Good, because Predictable resource ceiling
* Good, because Simpler capacity planning
* Bad, because May saturate at peaks
* Bad, because Can waste idle capacity
