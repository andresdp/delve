# Scale stateless scoring workers horizontally

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue working during peaks while returning scores quickly. Stateless workers can be replicated to add inference capacity without coordinating per-transaction state.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Horizontally scaled stateless workers
* Single larger scoring server

## Decision Outcome

Chosen option: "Horizontally scaled stateless workers".

Replicated workers provide a straightforward way to add inference capacity during peaks and avoid a single scoring host as the sole failure point.

### Consequences

* Requests need distribution across workers.
* Shared feature and model dependencies must also support peak load.

## Pros and Cons of the Options

### Horizontally scaled stateless workers

* Good, because Add capacity by replication
* Good, because Simple request distribution
* Bad, because Needs shared dependencies
* Bad, because Capacity planning required

### Single larger scoring server

* Good, because Simple deployment
* Good, because No distribution layer
* Bad, because Capacity ceiling
* Bad, because Single failure point
