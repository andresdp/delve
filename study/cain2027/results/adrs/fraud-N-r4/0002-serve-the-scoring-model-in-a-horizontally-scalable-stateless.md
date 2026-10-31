# Serve the scoring model in a horizontally scalable stateless tier

* System: Card-fraud scoring service

## Context and Problem Statement

The service must return scores quickly and keep working during traffic peaks.

## Decision Drivers

* Low latency
* Peak availability
* Per-transaction scoring

## Considered Options

* Horizontally scaled stateless serving
* Single centralized scoring instance
* Embedded model in authorization services

## Decision Outcome

Chosen option: "Horizontally scaled stateless serving".

A replicated serving tier can scale with peaks and avoid a single scoring bottleneck while keeping model serving separate from authorization components.

### Consequences

* Serving instances need consistent model artifacts
* Scaling and health monitoring are required

## Pros and Cons of the Options

### Horizontally scaled stateless serving

* Good, because Scale out with demand
* Good, because Instances can be replaced
* Bad, because Requires replicated model artifacts
* Bad, because Feature access may add latency

### Single centralized scoring instance

* Good, because Simple deployment
* Good, because No model replication
* Bad, because Capacity bottleneck
* Bad, because Single failure point

### Embedded model in authorization services

* Good, because Avoids network hop
* Good, because Local availability
* Bad, because Couples model releases to callers
* Bad, because Harder to centralize version tracking
