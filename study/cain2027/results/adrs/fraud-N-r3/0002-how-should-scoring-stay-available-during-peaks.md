# How should scoring stay available during peaks?

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction needs scoring, and the service is expected to keep working during peaks. The brief does not specify traffic shape or deployment platform.

## Decision Drivers

* Continuous scoring
* Peak resilience
* Low latency

## Considered Options

* Replicated stateless scoring instances
* Single scoring instance

## Decision Outcome

Chosen option: "Replicated stateless scoring instances".

Replicated instances can serve requests in parallel and keep scoring available when an instance fails. Statelessness supports scaling without coordinating request state.

### Consequences

* Model and configuration must be available to each instance.
* Capacity and health monitoring are required.

## Pros and Cons of the Options

### Replicated stateless scoring instances

* Good, because Scale out with demand
* Good, because Instance failures tolerated
* Bad, because Requires capacity management

### Single scoring instance

* Good, because Simple deployment
* Good, because No coordination
* Bad, because Single failure point
* Bad, because Limited peak capacity
