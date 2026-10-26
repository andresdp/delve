# Replicated stateless instances with autoscaling

*How should the service handle peaks and failures?*

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring path must keep working during peaks. The brief does not specify a capacity target or degradation policy.

## Decision Drivers

* Peak resilience
* Low latency

## Considered Options

* Replicated stateless instances with autoscaling
* Fixed overprovisioned capacity
* Queue transactions for scoring

## Decision Outcome

Chosen option: "Replicated stateless instances with autoscaling".

Peak resilience decides the choice: additional instances can handle sustained load while keeping scoring synchronous. This gives up the cost efficiency of fixed sizing and cannot guarantee coverage for sudden bursts before scaling completes.

### Consequences

* Capacity depends on scaling behavior and available compute.
* Replica health and model consistency need operational monitoring.

## Pros and Cons of the Options

### Replicated stateless instances with autoscaling

* Good, because Peak resilience: adds serving capacity
* Bad, because Low latency: scaling may lag sudden bursts

### Fixed overprovisioned capacity

* Good, because Peak resilience: ready capacity for bursts
* Bad, because Cost: pays for idle capacity

### Queue transactions for scoring

* Good, because Peak resilience: absorbs bursts
* Bad, because Low latency: queueing delays authorization
