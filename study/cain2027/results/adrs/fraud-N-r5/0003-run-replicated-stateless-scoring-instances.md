# Run replicated stateless scoring instances

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during traffic peaks. Stateless instances can be scaled horizontally and replaced without coordinating local transaction state.

## Decision Drivers

* Peak availability
* Variable transaction load
* Low latency

## Considered Options

* Replicated stateless instances
* Single scoring instance

## Decision Outcome

Chosen option: "Replicated stateless instances".

Replicas provide capacity for peaks and reduce the impact of an individual instance failure. This choice depends on shared feature and model dependencies also having suitable availability.

### Consequences

* Requires load balancing
* Peak capacity must be provisioned

## Pros and Cons of the Options

### Replicated stateless instances

* Good, because Horizontal scaling
* Good, because Instance failure isolation
* Bad, because Needs capacity management
* Bad, because Shared dependencies remain

### Single scoring instance

* Good, because Simple deployment
* Good, because No coordination overhead
* Bad, because Single failure point
* Bad, because Limited peak capacity
