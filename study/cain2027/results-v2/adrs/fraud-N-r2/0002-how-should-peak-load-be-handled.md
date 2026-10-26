# How should peak load be handled?

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during transaction peaks. The brief gives no traffic profile or capacity target, so the design must allow capacity to be added without assuming a specific scale.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Fixed-capacity deployment
* Replicated, horizontally scalable deployment

## Decision Outcome

Chosen option: "Replicated, horizontally scalable deployment".

Peak availability is explicit and ranks ahead of minimizing operational overhead, so replicas are the better fit; this gives up deployment simplicity.

### Consequences

* Provision and monitor multiple serving instances.
* Define scaling and overload behavior.

## Pros and Cons of the Options

### Fixed-capacity deployment

* Good, because Low latency: avoids scaling delays
* Bad, because Peak availability: overload can cause timeouts

### Replicated, horizontally scalable deployment

* Good, because Peak availability: distributes load across instances
* Bad, because Low latency: scaling and coordination add operational overhead
