# Make scoring capacity independent of individual requests

* System: Card-fraud scoring service

## Context and Problem Statement

Peak resilience and low latency favor serving requests across interchangeable instances instead of depending on one process's local state.

## Decision Drivers

* Peak resilience
* Low latency
* Horizontal scaling

## Considered Options

* Load models into interchangeable instances
* Route requests to stateful model owners

## Decision Outcome

Chosen option: "Load models into interchangeable instances".

Interchangeable instances allow requests to be spread across capacity during peaks and simplify replacing unhealthy instances.

### Consequences

* Instances need access to the same model versions.
* Rollouts must preserve version attribution for in-flight scores.

## Pros and Cons of the Options

### Load models into interchangeable instances

* Good, because Requests can use available capacity
* Good, because Instance replacement is straightforward
* Bad, because Model rollout must be coordinated

### Route requests to stateful model owners

* Good, because Can reuse local state
* Bad, because Creates routing dependencies
* Bad, because Uneven load risk
